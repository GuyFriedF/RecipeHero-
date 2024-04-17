#import pandas as pd
#import csv
#import numpy as np
#import streamlit as st

url = "https://drive.google.com/file/d/1OMZf5eUXRiagsSVQ_Q-ETt8_m3c33K-p/view?usp=sharing"
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
df = pd.read_csv(path,engine='python', on_bad_lines='skip')





#Creating lists in the dataframe for better matching:

listy=[]   #empty list to be filled with ingredeints names

for i in range(len(df)):
  x = df.iloc[i]['ingredients'].strip("[]").replace(r'"',"").replace(r"'","").split(", ")  #using the split method to create a list of ingredients
  listy.append(x)  #appending each list to the empty list, creating a list of lists

df['ingredients_list']=listy   #adding the new column to the database

# Adding an "Ingredients" column that is composed of lists to the database, for easier matching


listx=[]   #empty list to be filled different recipe steps:

for i in range(len(df)):
  listz=[]
  x = df.iloc[i]['steps'].strip("[]").split("', '")  #using the split method to create a list of ingredients
  for j in x:
    y = j.replace(r'"',"").replace(r"'","")
    listz.append(y)
  listx.append(listz)  #appending each list to the empty list, creating a list of lists

df['steps_list']=listx   #adding the new column to the database

#Creating 'Dietary' and 'Gluten' labels, and adding them to the database:

df['dietary'] = 'vegan'    #Assuming all recipes are 'Vegan', unless they contain animal products, then they become either 'Vegeterian' or 'None' (meaning a person has no dietary restrictions/Omnivore)
df['gluten'] = 'gluten-free'

diet_list = {"vegeterian":['butter','milk','whole milk','cream','cheese','feta','eggs','parmesan',
             'buttermilk','mayonaise','mayonnaise','yoghurt'],
             "none":['beef','sirloin','chicken','fish','shrimp','octopus','ground beef',
             'bacon','salmon','lamb','pork','sausage','anchovies','meat','crab',' ham'],
            }
not_glutenfree = ['bread','pasta','flour','pizza','crust','cracker','wheat']   #If any recipe contains these ingredients, they are not Gluten-Free

for i in diet_list:     #Iterating over the 'Dietary' dictionary, looking whether any recipe in the database contains any of the values inside in each key
  for j in diet_list[i]:
    df.loc[df['ingredients'].str.contains(j), 'dietary'] = i
    df.loc[df['name'].str.contains(j), 'dietary'] =i


for i in not_glutenfree:
  df.loc[df['ingredients'].str.contains(i), 'gluten'] = "not gluten-free"
  df.loc[df['name'].str.contains(i), 'gluten'] = "not gluten-free"
# Turning string-based 'dietary' column to lists

rest_list=[]   #empty list to be filled

for i in range(len(df)):
  a = df.iloc[i]['dietary'].split(",")  #using the split method to create a list of dietary restrictions
  b= set(a)
  c= list(b)
  rest_list.append(c)  #appending each list to the empty list, creating a list of lists

df['dietary']=rest_list


#Creating a list of all unique ingredeints in the recipes database, sorting them alphabetically, to be used in the multiselect drop-down menu
temp=df['ingredients_list'].explode().unique()
temp2 = list(temp)
temp3 = np.sort(temp2)
allingred = list(temp3)
#this list will be used to make sure that user input has to match available ingredeints in the database


#Setting values to session state:

if 'currentdf' not in st.session_state:
  st.session_state.currentdf = df
if 'min_n' not in st.session_state:
  st.session_state.min_n = 1
if 'max_n' not in st.session_state:
  st.session_state.max_n = 50
if 'min_step' not in st.session_state:
  st.session_state.min_step = 1
if 'max_step' not in st.session_state:
  st.session_state.max_step = 50
if 'min_time' not in st.session_state:
  st.session_state.min_time = 1
if 'max_time' not in st.session_state:
  st.session_state.max_time = 200

df1 = ""



#Define some functions to be used in the script

def df_update(df):
  st.session_state.currentdf = df

def minmax(df, column):
  min=df[column].min()
  max=df[column].max()
  return min, max

def match_ingredients(df, igdlist):
  var=len(igdlist)
  temp = df[df['ingredients_list'].apply(lambda x: any(ingredient in igdlist for ingredient in x))]   #check if any ingredient from user-input is found in ingredeints list, per each recipe
  temp['matches'] = temp['ingredients_list'].apply(lambda x: sum(1 for ingredient in x if ingredient in igdlist)) #create a new column 'match', and then  increase it's value by 1 each time an ingredient from user-input is found in ingredeints list
  result = temp.loc[temp['matches']>=(var/2)]
  result = result.sort_values('matches', ascending=False)
  df_update(result)
  return result

def match_style(df,params, restrict, gluten):
  result=df[df['style'].apply(lambda x: any(ingredient in x for ingredient in params))]
  result2 = result[result['dietary'].apply(lambda x: any(ingredient in x for ingredient in restrict))]
  result3 = result2[result2['gluten'].apply(lambda x: any(ingredient in x for ingredient in gluten))]
  df_update(result3)
  return result3

def match_dietary(df,params):
  result=df[df['dietary'].apply(lambda x: any(ingredient in x for ingredient in params))]
  df_update(result)
  return result


def match_steps(df, values):
  result=df.loc[df['n_steps'].between(values[0],values[1])]
  result = result.sort_values('matches', ascending=False)
  df_update(result)
  return result

def match_num(df,values):
  result=df.loc[df['n_ingredients'].between(values[0],values[1])]
  df_update(result)
  return result

def match_time(df, values):
  result=df.loc[df['minutes'].between(values[0],values[1])]
  df_update(result)
  return result




# Title
st.title("RecipeHero!")

# Dropdown menu
with st.container():
  st.subheader("Ingredients:")
  st.session_state.currentdf = df
  dropdown_value = st.multiselect("Please type in your ingredients:", allingred, on_change=df_update, args=[df])
  st.session_state.currentdf = match_ingredients(df, dropdown_value)
  df2 =df1


#st.session_state

stylist=['italian', 'french',
  'mexican','asian', 'american', 'oriental',
  'greek', 'spanish', 'soup','breakfast','salad', 
  'dessert','bread','drinks','dips & dressing']
with st.container():
  st.subheader("Style and Dietary-restrictions:")
  params = st.multiselect("Please choose which style of recipes you would like:", ['italian', 'french',
  'mexican','asian', 'american', 'oriental',
  'greek', 'spanish', 'soup','breakfast','salad', 
  'dessert','bread','drinks','dips & dressing','any'],default=['any'], on_change=df_update, args=[st.session_state.currentdf])
  restrict = st.multiselect("Do you have any dietary restrictions?", ['none','vegan','vegeterian', 'gluten-free'], default=['none'], on_change=df_update, args=[st.session_state.currentdf])
  if 'gluten-free' in restrict:
    if params==['any']:
      try:
        st.session_state.currentdf = match_style(st.session_state.currentdf, stylist, restrict, 'gluten-free')
      except:
        st.write("Waiting for values...")
    else:
      try:
        st.session_state.currentdf = match_style(st.session_state.currentdf, params, restrict, 'gluten-free')
      except:
        st.write("Waiting for values...")
  else:
    if params==['any']:
      try:
        st.session_state.currentdf = match_style(st.session_state.currentdf, stylist, restrict, 'not gluten-free')
      except:
        st.write("Waiting for values...")
    else:
      try:
        st.session_state.currentdf = match_style(st.session_state.currentdf, params, restrict, 'not-glutenfree')
      except:
        st.write("Waiting for values...")
  df2=df1

with st.container():
  st.subheader("Number of ingredients, steps and time:")
  col1, col2, col3 = st.columns(3)
  with col1:
    try:
      st.session_state.min_n, st.session_state.max_n = minmax(st.session_state.currentdf,'n_ingredients')
      values = st.slider(
      'Select the number of ingredients',
      min_value=st.session_state.min_n, max_value=st.session_state.max_n,value=[st.session_state.min_n,st.session_state.max_n])
      st.session_state.currentdf = match_num(st.session_state.currentdf, values)
      df2=df1
    except:
      st.write("Waiting for values...")
      tempvalues = st.slider(
      'Select the number of ingredients',
      min_value=1, max_value=25,value=[1,25])
  with col2:
    try:
      st.session_state.min_step , st.session_state.max_step = minmax(st.session_state.currentdf,'n_steps')
      stepvalues = st.slider(
      'Select the number of steps',
      min_value=st.session_state.min_step, max_value=st.session_state.max_step,value=[st.session_state.min_step,st.session_state.max_step])
      st.session_state.currentdf = match_steps(st.session_state.currentdf,stepvalues)
      df2=df1
    except:
      st.write("Waiting for values...")
      tempvalues2 = st.slider(
      'Select the number of steps',
      min_value=1, max_value=25,value=[1,25])

  with col3:
    try:
      st.session_state.min_time, st.session_state.max_time = minmax(st.session_state.currentdf,'minutes')
      values3 = st.slider(
      'Select the number of minutes',
      min_value=st.session_state.min_time, max_value=st.session_state.max_time,value=[st.session_state.min_time,st.session_state.max_time])
      st.session_state.currentdf = match_time(st.session_state.currentdf, values3)
      df2=df1
    except:
      st.write("Waiting for values...")
      tempvalues3 = st.slider(
      'Select the number of minutes',
      min_value=0, max_value=300,value=[1,300])





with st.container():
  st.subheader("Recipes results:")
  number = st.number_input("How many recipes should be shown",min_value=1)

  button = st.button("Show results")
  if button:
    if number<len(st.session_state.currentdf.index):
      df2=st.session_state.currentdf.sample(number)
      tablist = []
      for i in list(range(number)):
        tabstr = df2.iloc[i]['name']
        tablist.append(tabstr)

    else:
      tablist = []
      df2 = st.session_state.currentdf
      for i in list(range(len(df2.index))):
        tabstr = df2.iloc[i]['name']
        tablist.append(tabstr)

    try:
      tabs =  st.tabs(tablist)
      for i,tab in enumerate(tabs):
        with tab:
          xy = str(tablist[i])
          xz = df2.loc[st.session_state.currentdf['name']==xy]
          cola, colb = st.columns(2)
          with cola:
            st.write("Ingredients:")
            for j in xz['ingredients_list']:
              st.write(j)
          with colb:
            st.write("Steps:")
            for i in xz['steps_list']:
              st.write(i)
    except:
      st.write("No matching recipes. Please try another combination.")
