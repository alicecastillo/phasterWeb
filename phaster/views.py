from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib import messages

# packages needed to run phaster
import os, subprocess, json, re
from collections import defaultdict
from urllib.request import urlopen
import pandas as pd

from .phaster_classes import PhasterJSON

# from .models import Keyword
from .forms import SearchField


jsonFile = "phaster_io_output.txt"
runTimes = 0
pausedAccessions = []


# runs the scrape of given url
def runScrape(url):
    wp = urlopen(url)
    html_bytes = wp.read()
    html = html_bytes.decode("utf-8")
    return html

def runPhaster(seq, badAccessions):
    link = ("http://phaster.ca/phaster_api?acc=%s" %(seq))
    osLink = ("wget \"%s\" -O %s" %(link, jsonFile))
    
    info = os.system(osLink)
    summ = getPhasterJson(seq)
    if summ:
        # runTimes += 1
        # print("RUN {} TIMES; this was {}".format(runTimes, seq))
        # print("*******")
        return summ
    else:
        badAccessions.append(seq)
        print("DELAYED FOR {}".format(seq))
        # time.sleep(61)
        return False


def getPhasterJson(seq):
    with open(jsonFile) as f:
        json_data = json.load(f)
    try:
        obj = PhasterJSON(json_data)
        summary = obj.summary.split("-----------",1)
        summary_large = cleanSummary(summary[1])
        return summary_large
    except Exception as e:
        print("ERROR: {}".format(e))
        return False


def cleanSummary(summary):
    phaster_io_keys = ["REGION", "REGION_LENGTH", "COMPLETENESS(score)", "SPECIFIC_KEYWORD", "REGION_POSITION", "TRNA_NUM", 
    "TOTAL_PROTEIN_NUM", "PHAGE_HIT_PROTEIN_NUM", "HYPOTHETICAL_PROTEIN_NUM", "PHAGE+HYPO_PROTEIN_PERCENTAGE", "BACTERIAL_PROTEIN_NUM", 
    "ATT_SITE_SHOWUP", "PHAGE_SPECIES_NUM", "MOST_COMMON_PHAGE_NAME(hit_genes_count)", "FIRST_MOST_COMMON_PHAGE_NUM", 
    "FIRST_MOST_COMMON_PHAGE_PERCENTAGE", "GC_PERCENTAGE"]
    summarySplit = summary.split('\n')
    summarySplit.pop(0)
    cleanDict = dict.fromkeys(phaster_io_keys)
    cleaned = []
    for count, region in enumerate(summarySplit):
        details = region.split()
        cleanThis = dict.fromkeys(phaster_io_keys)
        if len(details) > 1:
            for val, key in enumerate(list(cleanThis.keys())):
                cleanThis[key] = details[val]
            cleaned.append(cleanThis)

    return cleaned


def retrieve(query_name):
    # generic script
    entrez_script = "esearch -db assembly -query \"[NAME]\" | elink -target nuccore | efetch -format docsum | xtract -pattern DocumentSummary -element AccessionVersion Genome Title > "

    # if 1+ spaces, replace with single space
    query_name = ' '.join(query_name.split())
    test_url = "https://www.ncbi.nlm.nih.gov/assembly/?term={}".format(query_name.strip().replace(" ", "+"))
    
    search_html = runScrape(test_url)

    invalid_search_items = re.search(r'not found in Assembly: (.*)\.', search_html, re.MULTILINE)
    
    if invalid_search_items:
        search_errors = invalid_search_items.group(0)
        search_errors = search_errors.split(":")[1].split("<")[0]
        search_error_list = [f.strip() for f in search_errors.split(",")]

        if len(search_error_list) > 1:
            print("ERROR: the following search terms were not recognized: ")
            print(", ".join(search_error_list))
        else:
            print("ERROR: the following search term was not recognized: ")
            print(search_error_list[0])
        return "", query_name, search_error_list[0]

    else:
        # replace areas of script
        output_file_path = "entrez_output_{}.txt".format(query_name.replace(" ", ""))
        entrez_script = entrez_script.replace("[NAME]", query_name) + output_file_path
        print("ENTREZ SCRIPT: {}".format(entrez_script))
        # run entrez query
        os.system(entrez_script)
        return output_file_path, query_name, ""

def save_post_data(request, post):
    print("saving post data")
    request.session['accession_only'] = post['accession_number_only']
    request.session['keyword'] = post['keyword']
    request.session.modified = True



def runFullPhaster(keyword, accession_only):
    badAccessions = []
    valid_entrez, query, bad_input = retrieve(keyword)

    if bad_input:
        return "", "", bad_input

    if valid_entrez:
        f = open(valid_entrez, "r")
        query_res = f.read()
        access_blocks = query_res.split("\n")
        access_blocks = [f for f in access_blocks if f]

        access_dict = defaultdict(list)
        for ab in access_blocks:
            if "NZ_" not in ab and len(ab) > 1:
                # accession, genome, title
                ab_items = ab.split("\t")
                ab_values = ab_items[1:len(ab_items)]
                ab_key = ab_items[0]

                # retrieve primary accession via scrape
                try:
                    test_url = "https://www.ncbi.nlm.nih.gov/assembly/?term={}".format(ab_key.strip())
                    search_html = runScrape(test_url)
                    prim_accession = re.search(r'RefSeq assembly accession:(.*)RefSeq assembly', search_html, re.MULTILINE)
                    prim_accession = prim_accession.group(0).split("<dd>")[1].split("<")
                    prim_accession = prim_accession[0].split(" ")[0]
                    ab_values.append(prim_accession)
                    access_dict[ab_key] = ab_values
                except Exception as e:
                    print("{} ERROR: {}".format(ab_key, e))
                    ab_values.append("[NOT FOUND]")
                    access_dict[ab_key] = ab_values


        df_list = []
        error_list = []
        for key, value in access_dict.items():
            summary_list = runPhaster(key, badAccessions)
            if summary_list:
                for summary in summary_list:
                    df_dict = {}
                    df_dict["ID"] = value[2]
                    df_dict["Name"] = value[1].split(",")[1].strip()
                    df_dict["Type"] = value[0]
                    df_dict["Accession"] = key
                    df_dict["Region"] = summary["REGION"]
                    df_dict["Region Length"] = summary["REGION_LENGTH"]
                    comp_score = summary["COMPLETENESS(score)"].split("(")
                    df_dict["Completeness"] = comp_score[0]
                    df_dict["Completeness Score"] = comp_score[1].replace(")", "")
                    df_dict["# Total Proteins"] = summary["TOTAL_PROTEIN_NUM"]
                    df_dict["Region Position"] = summary["REGION_POSITION"]
                    mcp = summary["MOST_COMMON_PHAGE_NAME(hit_genes_count)"].split(',')[0]
                    if "(" in mcp:
                        mcp_list = mcp.split("(")
                        df_dict["Most Common Phage (MCP)"] = mcp_list[0]
                        df_dict["MCP Occurrences"] = mcp_list[1].replace(")", "")
                    else:
                        df_dict["Most Common Phage (MCP)"] = mcp
                        df_dict["MCP Occurrences"] = None
                    df_dict["GC %"] = summary["GC_PERCENTAGE"]
                    df_dict["Details"] = "None"
                    df_list.append(df_dict)
            else:
                print("ERROR for {}".format(key))
                error_dict = {}
                error_dict["ID"] = value[2]
                error_dict["Accession"] = key
                error_dict["Error"] = "Phaster API backlogged"
                error_list.append(error_dict)

        # send output (and errors, if any) to file
        final_df = pd.DataFrame(df_list)
        query_excel = query.replace(" ", "_").replace("-", "")
        print("/Users/alicecastillo/Desktop/phaster_run_{}.xlsx".format(query_excel))
        user_profile = os.environ.get('USERPROFILE')
        excel_path = "{}/Desktop/phaster_run_{}.xlsx".format(user_profile, query_excel)
        writer = pd.ExcelWriter(path="/Users/alicecastillo/Desktop/phaster_run_{}.xlsx".format(query_excel), engine='xlsxwriter')
        final_df.to_excel(writer, sheet_name = "Successful Accession Runs", index=False)
        if error_list:
            error_df = pd.DataFrame(error_list)
            error_df.to_excel(writer, sheet_name="Errors", index=False)
            print("Accessions not reached: {}".format(badAccessions))
        writer.save()
        f.close()
        try:
            os.remove(valid_entrez)
        except Exception as e:
            print("Error while trying to delete entrez output: {}".format(e))
        return excel_path, error_list, ""
    return "", "", "Entrez output could not be found"
        

#### VIEWS ############################################################################################################
    
def homepage(request):
    print(request.GET)
    form = SearchField()
    if request.POST:
        req = SearchField(request.POST)
        print(req)
        if req.is_valid():
            print("valid submission")
            req = req.cleaned_data
            print(req)
            # save_post_data(request, req)
            print("POST DATA WAS SAVED")
            # keyword.replace(" ", "_")
            excel_path, error_list, warning_msg = runFullPhaster(req['keyword'], req['accession_number_only'])
            if warning_msg:
                warning_msg = "Unrecognized search words: {}".format(req["keyword"], warning_msg)
                return render(request,'phaster/homepage.html', {'form':SearchField(), 'warning_msg':warning_msg})
            elif excel_path:
                if error_list:
                    file_created = "File '{}' added to your Desktop, but some accession numbers were not run :(".format(excel_path.split("/")[-1])
                else:
                    file_created = "File '{}' added to your Desktop. All accession numbers ran successfully :)".format(excel_path.split("/")[-1])
                return render(request,'phaster/homepage.html', {'form':SearchField(), 'file_created':file_created})
            else:
                warning_msg = "An unknown error occurred. Please try again, and if the problem persists contact Alice."
                return render(request,'phaster/homepage.html', {'form':SearchField(), 'warning_msg':warning_msg})

    else:
        form = SearchField()
    return render(request,'phaster/homepage.html', {'form':form})


def results(request):
    # print(request.session.get('accession_only'))
    # print(request.session.get('keyword'))
    def get_queryset(self):
        keyword = self.kwargs['keyword'].replace('_',  ' ')
    
        print("full throttle ahead")

    return render(request,'phaster/results.html') #, {'form':form})


class UsageView(generic.TemplateView):
    # model = Keyword
    template_name = 'opi_api/usage.html'
