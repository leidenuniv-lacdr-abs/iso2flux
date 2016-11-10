import csv
from openpyxl import load_workbook
import re
import Tkinter
import tkFileDialog
from ..misc.read_spreadsheets import read_spreadsheets
import numpy

if __name__=="__main__":
   from iso2flux.misc.read_spreadsheets import read_spreadsheets

def read_metabolights(label_model,file_name,selected_condition="Ctr",selected_time=18,minimum_sd=0.01,rsm=True):
   label_model.minimum_sd=minimum_sd
   #TODO account for multiple time units
   emu0_dict={}
   label_model.experimental_dict={}
   label_model.data_name_emu_dict={}
   name_id_dict={}
   for x in label_model.metabolic_model.metabolites:
       if x.name==None or x.name=="":
          x.name=x.id
       if x.name.lower() not in  name_id_dict:
          name_id_dict[x.name.lower()]=[]
       name_id_dict[x.name.lower()].append(x.id)
   sheet_rows_dict=read_spreadsheets(file_names=file_name,csv_delimiter=',',more_than_1=False,tkinter_title="") 
   for sheet in sheet_rows_dict:
       #Identfy the contents of each col
       col_n_dict={}
       rows=sheet_rows_dict[sheet]
       for n,header in enumerate(rows[0]):
           if header!=None:
              col_n_dict[header.lower()]=n #Remove caps
       print col_n_dict
       #Update this if the headers are changed
       labelled_substrate_emuid_isotopologue_replicate_injection_dict={}
       n_condition=col_n_dict["conditions"]
       n_substrate=col_n_dict["labelled substrate"]
       n_lab_pattern_substrate=col_n_dict["label pattern"]  
       #n_lab_sub_abundance=col_n_dict["abundance [value]"]
       n_lab_sub_abundance=col_n_dict["abundance"]
       #n_lab_sub_abundance_units=col_n_dict["abundance [units]"]
       n_time=col_n_dict["incubation time [value]"]
       n_replicate=col_n_dict["replicate"]
       n_injection=col_n_dict["injection"]
       n_metabolite_name=col_n_dict["metabolite name"]
       n_carbon_range=col_n_dict["atomic positions to the parent molecule/metabolite name"]
       n_isotopologue=col_n_dict["isotopologue"]
       n_isotopologue_abundance=col_n_dict["isotopologue [value]"]
       #n_isotopologue_units=col_n_dict["isotopologue [units]"]
       n_isotopologue_units=col_n_dict["isotopologue [units]"]
       for n,row in enumerate(rows):
           if n==0:
              continue
           condition=row[n_condition]
           metabolite_name=str(row[n_metabolite_name])
           unrpocessed_carbon_range=row[n_carbon_range].lower()
           str_isotopologue=row[n_isotopologue]
           replicate=str(row[n_replicate])
           injection=str(row[n_injection])
           print [replicate,injection]
           substrate=row[n_substrate]
           abundance=row[n_lab_sub_abundance]
           pattern=row[n_lab_pattern_substrate]
           isotopologue_abundance_str=row[n_isotopologue_abundance]
           if  any(x==None or x=="" for x in [abundance,pattern,substrate,metabolite_name,unrpocessed_carbon_range,str_isotopologue,replicate,injection,isotopologue_abundance_str]):
               continue
               #print "aaaaaaaaaaAAaa"
           #print "bbbbbbbb"
           time=float(row[n_time])
           print [[condition,selected_condition],[time,float(selected_time)]]
           if condition!=selected_condition or time!=float(selected_time):
              #print "ccccccccccccccccccccc"
              continue 
           #print "ddddddddddddddddd"
           """if row[n_lab_sub_abundance_units]=="%":
              abundance/=100"""
           labelled_substrate=str(substrate)+"$/$"+str(pattern)+"$/$"+str(abundance)
           isotopologue=str(row[n_isotopologue].lower().replace("m","")) 
           print [n_isotopologue,row[n_isotopologue],isotopologue]
           isotopologue_abundance=float(row[n_isotopologue_abundance])
           if row[n_isotopologue_units]=="%":
              isotopologue_abundance/=100 
           #Define Emus
           metabolite_id=name_id_dict[metabolite_name.lower()][0] #Assume that so far all metabolites are the same label pool regardles of the compartment
           carbon_range=unrpocessed_carbon_range.replace("c","").split("-")
           if len(carbon_range)>1: 
                  carbons=[x for x in range(int(carbon_range[0]),int(carbon_range[1])+1)]
           else:
                  carbons=[int(carbon_range[0])]
           local_emu0_dict={}
           if metabolite_id in label_model.met_id_isotopomer_dict:
                  iso_object=label_model.met_id_isotopomer_dict[metabolite_id]
           else:
                  print (metabolite_id+" not defined as isotopomer")
           emuid="emu_"+iso_object.id+"_"
           print emuid
           local_emu0_dict["done"]=False
           local_emu0_dict["size"]=len(carbons)
           local_emu0_dict["met_id"]=iso_object.id
           local_emu0_dict["carbons"]=carbons
           carbon_range_string=""
           for carbon in sorted(carbons):  
                   carbon_range_string+=str(carbon)
           if iso_object.symm==True:
                  #build a symetryc dic
                  symm_dict={}
                  forward_range=range(1,iso_object.n+1)
                  reverse_range=range(iso_object.n,0,-1)
                  for x in forward_range:
                      symm_dict[x]=reverse_range[x-1]
                  #print symm_dict
                  symm_carbons=[]
                  for carbon in carbons:
                      symm_carbons.append(symm_dict[carbon])
                  #print symm_carbons
                  symm_carbons=sorted(symm_carbons) 
                  local_emu0_dict["symm_carbons"]=symm_carbons
                  if symm_carbons!=carbons: #Check if they are not equal: 
                     #Identfy the lower range, which will be written first in the metabolite id
                     symm_carbon_range_string="" 
                     for carbon in symm_carbons:
                         symm_carbon_range_string+=str(carbon)
                      
                     if symm_carbons[0]<carbons[0]:
                        emuid+=symm_carbon_range_string+"_and_"+carbon_range_string
                     else:
                        emuid+=carbon_range_string+"_and_"+symm_carbon_range_string
                  else:
                     local_emu0_dict["symm_carbons"]=[] 
                     emuid+=carbon_range_string
           else:
                     emuid+=carbon_range_string
           if emuid not in label_model.rsm_list and rsm==True:
                        label_model.rsm_list.append(emuid) 
           if emuid not in emu0_dict:  
                  emu0_dict[emuid]= local_emu0_dict
                  if emuid not in label_model.data_name_emu_dict:
                     label_model.data_name_emu_dict[emuid]=metabolite_name+"_"+unrpocessed_carbon_range
           if labelled_substrate not in labelled_substrate_emuid_isotopologue_replicate_injection_dict:
              labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate]={}
           if emuid not in labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate]:
              labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid]={}
           if isotopologue not in labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid]:
              labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid][isotopologue]={}
           if replicate not in labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid][isotopologue]:  
              labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid][isotopologue][replicate]=[]
           labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid][isotopologue][replicate].append(isotopologue_abundance)
   
   for labelled_substrate in labelled_substrate_emuid_isotopologue_replicate_injection_dict:
       initial_label=labelled_substrate.split("$/$")
       substrate_name=initial_label[0].lower()
       string_pattern=initial_label[1]
       abundance=float(initial_label[2]) 
       
       condition_name=(substrate_name+"_"+str(string_pattern)+"_"+str(round(abundance,4))).replace(" ","")
       substrate_id=name_id_dict[substrate_name][0]
       pattern=[int(x) for x in string_pattern.split(",") ]
       label_model.add_initial_label(substrate_id,[[pattern,abundance]],condition=condition_name,total_concentration=1)
       
       label_model.experimental_dict[condition_name]={}
       for emuid in labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate]:
           label_model.experimental_dict[condition_name][emuid]={}
           print labelled_substrate_emuid_isotopologue_replicate_injection_dict
           for mi in labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid]:
               data_dict=labelled_substrate_emuid_isotopologue_replicate_injection_dict[labelled_substrate][emuid][mi] 
               replicates_list=[numpy.mean(data_dict[replicates]) for replicates in data_dict]
               print replicates_list
               print data_dict
               mean=numpy.mean(replicates_list)
               sd=numpy.std(replicates_list)
               #sd=max(numpy.std(replicates_list),minimum_sd)
               print [emuid,mi]
               label_model.experimental_dict[condition_name][emuid][int(mi)]={"m":mean,"sd":sd}
   label_model.emu0_dict=label_model.emu_dict=emu0_dict
   return emu0_dict,label_model.experimental_dict 
