

!pip install prince


#IMPORTING LIBRARIES
import os #To manage files
import pandas as pd #to create panda dataframes
from google.colab import drive #to connect with Google Drive
import matplotlib.pyplot as plt #to plot graphs
import seaborn as sns; sns.set() #to plot graphs
from sklearn.model_selection import train_test_split # to split the dataset into train, validation and test datasets.
import matplotlib.ticker as mtick # to generate graphs
import numpy as np # linear algebra
from mpl_toolkits.mplot3d import Axes3D #to generate scatterplots
from sklearn.decomposition import PCA #to calculate Principal Component Analysis - PCA
import prince #to use multiple correspondece analysis - MCA
import plotly.graph_objs as go # for graphics
from plotly import tools #for graphics
import xgboost as xgb #to use XGBoost
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix, recall_score, matthews_corrcoef #to use evaluation metrics
import tensorflow as tf #to develop Autoencoder
from tensorflow import keras #to develop Autoencoder
from sklearn.neural_network import MLPClassifier #to train ANN - MLP
from sklearn.tree import DecisionTreeClassifier #to train Decision Tree
import time #to check the processing time
from sklearn.svm import LinearSVC #to operate with linear SVM
from sklearn.ensemble import RandomForestClassifier #to train Random Forest model.

# %matplotlib inline

#function to create dataframe for Autoencoder
def create_new_features_dataframe(feature_numpy_array, column_labbel, norm=False):
  if norm:
    input_ = normalize(feature_numpy_array)
  else:
    input_ = feature_numpy_array

  df = pd.DataFrame(input_)
  df.columns = ["{}_{}".format(column_labbel, idx) for idx, _ in enumerate(df.columns)]

  return df

#Function to plot graphs in browser.
def configure_plotly_browser_state():
  import IPython
  display(IPython.core.display.HTML('''
        <script src='/static/components/requirejs/require.js'></script>
        <script>
          requirejs.config({
            paths: {
              base: '/static/base',
              plotly: 'https://cdn.plot.ly/plotly-latest.min.js?noext',
            },
          });
        </script>
        '''))

#Setting up colab to connect with Google Drive
drive.mount('/content/drive')

#Setting up colab to deisplay all rows.
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


"""**Creation of the dataset.**"""

#Reading data files

data = pd.read_csv('./data.csv')
b_damage = pd.read_csv('./b_damage.csv')
b_use = pd.read_csv('./b_use.csv')

#Creating 'collapse' feauture from b_damage, that will be the target.
for i in b_damage:
   b_damage.loc[b_damage['damage_overall_collapse'] == 'Moderate-Heavy', 'collapse'] = 1
   b_damage.loc[b_damage['damage_overall_collapse'] == 'Severe-Extreme', 'collapse'] = 1
   b_damage.loc[b_damage['damage_overall_collapse'] == 'Insignificant/light', 'collapse'] = 0
   b_damage.loc[b_damage['damage_overall_collapse'] == 'None', 'collapse'] = 0

b_damage['collapse'].describe()

#Adding 'collapse' feature from b_damage dataframe to main dataframe 'data', as the target feature.
data['Building_Collapse']=b_damage['collapse']

#Cheking b_use data.
b_use.info()

#Removing repeated and non-related features from b_use dataftrame, to add to whole dataset to 'data'.
b_use.drop(columns=['district_id', 'vdcmun_id', 'ward_id', 'legal_ownership_status', 'count_families'],  inplace=True)

#Adding b_use dataframe left features to main dataframe 'data'.
data = data.merge(b_use, on='building_id')

"""**Preprocessing of the dataset.**"""

#Removing instances with empty values in target feature.
data.drop(data[data.Building_Collapse.isnull()].index, inplace=True)

#Removing non-related features for this study.
data.drop(columns=['count_floors_pre_eq', 'count_floors_post_eq', 'height_ft_pre_eq', 'height_ft_post_eq', 'condition_post_eq', 'damage_grade', 'technical_solution_proposed'],  inplace=True)

#Looking for instances with empty values.
data_temp = data.isnull().sum().reset_index(name='count')
display(data_temp[data_temp['count'] > 0])

#Removing instances with empty values.
data.dropna(inplace=True)

#Checking if there are duplicate instances.
sum(data.duplicated())

data.shape

data.info()

#Heatmap of the correlation matrix 
plt.figure(figsize=(30,24))
plt.title('Correlation matrix of features', fontdict={'fontsize':10})
ax = sns.heatmap(data.corr(), annot=False, linewidths=0.1)

#Removing 
data.drop(columns=['district_id', 'vdcmun_id', 'ward_id'],  inplace=True)

#Converting the ID of the every instance 'Building_id' into a categorical variable.
#data['building_id'] = data.building_id.astype('object')

data.info()

data.shape

"""Converting categorical variables into numerical variables."""

data['land_surface_condition'].value_counts()
#This is categorical ordinal data.

#Converting 'land_surface-condition' from 'object' to numerical values.
for i in data:
   data.loc[data['land_surface_condition'] == 'Flat', 'inclination'] = 1
   data.loc[data['land_surface_condition'] == 'Moderate slope', 'inclination'] = 2
   data.loc[data['land_surface_condition'] == 'Steep slope', 'inclination'] = 3

data.drop(columns=['land_surface_condition'],  inplace=True)

data['roof_type'].value_counts() #This could be considered categorical ordinal data, as it can be understood as 'roof robustness', as the hardest material, the more robust the roof could be.

#Converting 'roof_type' from 'object' to numerical values.
for i in data:
   data.loc[data['roof_type'] == 'Bamboo/Timber-Light roof', 'roof_strength'] = 1
   data.loc[data['roof_type'] == 'Bamboo/Timber-Heavy roof', 'roof_strength'] = 2
   data.loc[data['roof_type'] == 'RCC/RB/RBC', 'roof_strength'] = 3

data.drop(columns=['roof_type'],  inplace=True)

data['position'].value_counts()
#This could be considered categorical ordinal data, as it can be understood as 'stability', that the more attached to other structures, the more stable.

#Converting 'roof_type' from 'object' to numerical values.
for i in data:
   data.loc[data['position'] == 'Not attached', 'stability'] = 1
   data.loc[data['position'] == 'Attached-1 side', 'stability'] = 2
   data.loc[data['position'] == 'Attached-2 side', 'stability'] = 3
   data.loc[data['position'] == 'Attached-3 side', 'stability'] = 4

data.drop(columns=['position'],  inplace=True)

data['foundation_type'].value_counts()
#This is categorical nominal data.

#Converting 'foundation_type' from 'object' to numerical values.
for i in data:
   data.loc[data['foundation_type'] == 'Mud mortar-Stone/Brick', 'F_Mud'] = int(1)
   data.loc[data['foundation_type'] != 'Mud mortar-Stone/Brick', 'F_Mud'] = int(0)
   data.loc[data['foundation_type'] == 'Bamboo/Timber', 'F_Bamboo'] = 1
   data.loc[data['foundation_type'] != 'Bamboo/Timber', 'F_Bamboo'] = 0
   data.loc[data['foundation_type'] == 'Cement-Stone/Brick', 'F_Cement'] = 1
   data.loc[data['foundation_type'] != 'Cement-Stone/Brick', 'F_Cement'] = 0
   data.loc[data['foundation_type'] == 'RC', 'F_RC'] = 1
   data.loc[data['foundation_type'] != 'RC', 'F_RC'] = 0
   data.loc[data['foundation_type'] == 'Other', 'F_Other'] = 1
   data.loc[data['foundation_type'] != 'Other', 'F_Other'] = 0

data.drop(columns=['foundation_type'],  inplace=True)

data['ground_floor_type'].value_counts()
#This is categorical nominal data.

#Converting 'ground_floor_type' from 'object' to numerical values.
for i in data:
   data.loc[data['ground_floor_type'] == 'Mud', 'G_Mud'] = 1
   data.loc[data['ground_floor_type'] != 'Mud', 'G_Mud'] = 0
   data.loc[data['ground_floor_type'] == 'RC', 'G_RC'] = 1
   data.loc[data['ground_floor_type'] != 'RC', 'G_RC'] = 0
   data.loc[data['ground_floor_type'] == 'Brick/Stone', 'G_Brick/Stone'] = 1
   data.loc[data['ground_floor_type'] != 'Brick/Stone', 'G_Brick/Stone'] = 0
   data.loc[data['ground_floor_type'] == 'Timber', 'G_Timber'] = 1
   data.loc[data['ground_floor_type'] != 'Timber', 'G_Timber'] = 0
   data.loc[data['ground_floor_type'] == 'Other', 'G_Other'] = 1
   data.loc[data['ground_floor_type'] != 'Other', 'G_Other'] = 0

data.drop(columns=['ground_floor_type'],  inplace=True)

data['other_floor_type'].value_counts()

#Converting 'other_floor_type' from 'object' to numerical values.
for i in data:
   data.loc[data['other_floor_type'] == 'TImber/Bamboo-Mud', 'O_Timber'] = 1
   data.loc[data['other_floor_type'] != 'TImber/Bamboo-Mud', 'O_Timber'] = 0
   data.loc[data['other_floor_type'] == 'Not applicable', 'O_NA'] = 1
   data.loc[data['other_floor_type'] != 'Not applicable', 'O_NA'] = 0
   data.loc[data['other_floor_type'] == 'Timber-Planck', 'O_Planck'] = 1
   data.loc[data['other_floor_type'] != 'Timber-Planck', 'O_Planck'] = 0
   data.loc[data['other_floor_type'] == 'RCC/RB/RBC', 'O_RCC'] = 1
   data.loc[data['other_floor_type'] != 'RCC/RB/RBC', 'O_RCC'] = 0

data.drop(columns=['other_floor_type'],  inplace=True)

data['plan_configuration'].value_counts()

#Converting 'plan_configuration' from 'object' to numerical values.
for i in data:
   data.loc[data['plan_configuration'] == 'Rectangular', 'P_Rectangular'] = 1
   data.loc[data['plan_configuration'] != 'Rectangular', 'P_Rectangular'] = 0
   data.loc[data['plan_configuration'] == 'Square', 'P_Square'] = 1
   data.loc[data['plan_configuration'] != 'Square', 'P_Square'] = 0
   data.loc[data['plan_configuration'] == 'L-shape', 'P_L-shape'] = 1
   data.loc[data['plan_configuration'] != 'L-shape', 'P_L-shape'] = 0
   data.loc[data['plan_configuration'] == 'Multi-projected', 'P_Multi'] = 1
   data.loc[data['plan_configuration'] != 'Multi-projected', 'P_Multi'] = 0
   data.loc[data['plan_configuration'] == 'T-shape', 'P_T-shape'] = 1
   data.loc[data['plan_configuration'] != 'T-shape', 'P_T-shape'] = 0
   data.loc[data['plan_configuration'] == 'Others', 'P_Others'] = 1
   data.loc[data['plan_configuration'] != 'Others', 'P_Others'] = 0
   data.loc[data['plan_configuration'] == 'U-shape', 'P_U-shape'] = 1
   data.loc[data['plan_configuration'] != 'U-shape', 'P_U-shape'] = 0
   data.loc[data['plan_configuration'] == 'E-shape', 'P_E-shape'] = 1
   data.loc[data['plan_configuration'] != 'E-shape', 'P_E-shape'] = 0
   data.loc[data['plan_configuration'] == 'Building with Central Courtyard', 'P_BCC'] = 1
   data.loc[data['plan_configuration'] != 'Building with Central Courtyard', 'P_BCC'] = 0
   data.loc[data['plan_configuration'] == 'H-shape', 'P_H-shape'] = 1
   data.loc[data['plan_configuration'] != 'H-shape', 'P_H-shape'] = 0

data.drop(columns=['plan_configuration'],  inplace=True)

# Let's identify variables with a single value

no_variance_variables = []

for i in data.columns:
  if data[i].value_counts().values.shape[0] == 1:
    present_single_value = data[i].value_counts().index.values[0]
    print(f'Variable {i} has single value: {present_single_value}')
    no_variance_variables.append(i)

print(no_variance_variables)

data.describe()

data.shape

data.hist(column='age_building')

(data['age_building'] > 80).sum()

#As 'age_building' shows massive max values, all instances with a value more than a reasonable of less than 500 years, will be removed.
data.drop(data[data['age_building'] >= 80].index, inplace = True)

data.hist(column='age_building')

data.hist(column='plinth_area_sq_ft')

(data['plinth_area_sq_ft'] > 1500).sum()

data.drop(data[data['plinth_area_sq_ft'] >= 1500].index, inplace = True)

data.hist(column='plinth_area_sq_ft')

#Applying Max-Min scalling to the dataset, for a better performance in visualisation and experiments.
for i in data.columns:
    data[i] = (data[i] - data[i].min()) / (data[i].max() - data[i].min())

data.describe()

"""**Creating training, validation and test datasets**"""

#Splitting the dataset into train, validation (val) and test datasets.
train, test = train_test_split(data, test_size=0.4, random_state=20)

train.shape

test.shape

train,val = train_test_split(train,test_size=0.2, random_state=15)

train.shape

val.shape

#The result of this section are 3 datasets: training, validation and test, with 240352, 60089 and 200294 instances, respectively, and 33 features,
#where Building_ID is the unique identifier for every building and the feature TARGET is the label for each building showing two categorical values: collapse or safe.

"""**EXPLORATORY ANALYSIS**"""

train.info()

#Heatmap of the correlation matrix 
plt.figure(figsize=(30,24))
plt.title('Correlation matrix for features in the trainig dataset', fontdict={'fontsize':8})
ax = sns.heatmap(train.corr(), annot=False, linewidths=0.1)

#List of correlated values between features and target.
train.corr()['Building_Collapse'].sort_values(ascending=False)

#Checking if the dataset is balanced
np.sum(train['Building_Collapse']) / train.shape[0]

#Distributon of the target values 'Building_Collapse'.
plt.figure(figsize=(10,5))
sns.countplot(data=train, x='Building_Collapse')
plt.title('Distribution of Building collapse values')
plt.xlabel('Building collapse: 1 if collapsing, 0 if stable')
plt.show()

#Histograms of the most 4 correlated features to target.
train.hist('has_superstructure_mud_mortar_stone')
train.hist('F_Mud')
train.hist('has_superstructure_cement_mortar_brick')
train.hist('G_RC')

#Histogram with target value by colour.
plt.figure(figsize=(7,4))
sns.countplot(x=train['has_superstructure_mud_mortar_stone'],hue=train['Building_Collapse'],palette='viridis')
plt.figure(figsize=(7,4))
sns.countplot(x=train['F_Mud'],hue=train['Building_Collapse'],palette='viridis')
plt.figure(figsize=(7,4))
sns.countplot(x=train['has_superstructure_cement_mortar_brick'],hue=train['Building_Collapse'],palette='viridis')
plt.figure(figsize=(7,4))
sns.countplot(x=train['G_RC'],hue=train['Building_Collapse'],palette='viridis')

#Percentage of values for the 4 most correlated variables with the target, that happen to be binary.
cols = [['has_superstructure_mud_mortar_stone', 'F_Mud'], ['has_superstructure_cement_mortar_brick', 
        'G_RC']]

fig, axes = plt.subplots(ncols = 2, nrows = 2, figsize = (20,20))
for i, c in enumerate(cols):
    train[c[0]].value_counts().plot.pie(autopct='%.1f%%', ax = axes[i][0])
    train[c[1]].value_counts().plot.pie(autopct='%.1f%%', ax = axes[i][1])
plt.show()

"""**FEATURE ENGINEERING.**"""

# Assigning datasets for calculation, splitting the training from target sets.
X_train = train.drop(columns=[ 'Building_Collapse'], axis=1)
y_train = train['Building_Collapse']
X_val = val.drop(columns=[ 'Building_Collapse'], axis=1)
y_val = val['Building_Collapse']
X_test = test.drop(columns=[ 'Building_Collapse'], axis=1)
y_test = test['Building_Collapse']

X_train.info()

#The numerical features are extracted and the remaining binary ones are converted into categorical data.
X_train_cat = X_train.drop(columns=['age_building','plinth_area_sq_ft','inclination', 'roof_strength', 'stability'],  inplace=False)
X_train_cat = X_train_cat.astype('category')

X_val_cat = X_val.drop(columns=['age_building','plinth_area_sq_ft','inclination', 'roof_strength', 'stability'],  inplace=False)
X_val_cat = X_val_cat.astype('category')

X_test_cat = X_test.drop(columns=['age_building','plinth_area_sq_ft','inclination', 'roof_strength', 'stability'],  inplace=False)
X_test_cat = X_test_cat.astype('category')

X_train_cat.info()

"""Multiple Correspondece Analysis - MCA"""

#The most correlative with target features are selected for the generation of the MCA.
X_train_cat_select=X_train_cat[{'has_superstructure_mud_mortar_stone', 'F_Mud', 'O_Timber', 'G_Mud', 'has_superstructure_bamboo','has_secondary_use_hotel', 'has_secondary_use_agriculture',  'has_superstructure_stone_flag', 'has_secondary_use_rental', 'G_RC', 'has_superstructure_timber', 'has_superstructure_cement_mortar_brick', 'F_Bamboo', 'O_NA', 'F_RC', 'O_RCC', 'has_superstructure_rc_engineered', 'F_Cement', 'has_superstructure_mud_mortar_brick', 'has_superstructure_rc_non_engineered'}]
X_val_cat_select=X_val_cat[{'has_superstructure_mud_mortar_stone', 'F_Mud', 'O_Timber', 'G_Mud', 'has_superstructure_bamboo','has_secondary_use_hotel', 'has_secondary_use_agriculture',  'has_superstructure_stone_flag', 'has_secondary_use_rental', 'G_RC', 'has_superstructure_timber', 'has_superstructure_cement_mortar_brick', 'F_Bamboo', 'O_NA', 'F_RC', 'O_RCC', 'has_superstructure_rc_engineered', 'F_Cement', 'has_superstructure_mud_mortar_brick', 'has_superstructure_rc_non_engineered'}]
X_test_cat_select=X_test_cat[{'has_superstructure_mud_mortar_stone', 'F_Mud', 'O_Timber', 'G_Mud', 'has_superstructure_bamboo','has_secondary_use_hotel', 'has_secondary_use_agriculture',  'has_superstructure_stone_flag', 'has_secondary_use_rental', 'G_RC', 'has_superstructure_timber', 'has_superstructure_cement_mortar_brick', 'F_Bamboo', 'O_NA', 'F_RC', 'O_RCC', 'has_superstructure_rc_engineered', 'F_Cement', 'has_superstructure_mud_mortar_brick', 'has_superstructure_rc_non_engineered'}]

X_train_cat_select.info()

#Generation of MCA with 2 dimensions for training, validation and test data.
train_mca = prince.MCA()
train_mca = train_mca.fit(X_train_cat_select) 
train_mca = train_mca.transform(X_train_cat_select)

val_mca = prince.MCA()
val_mca = val_mca.fit(X_val_cat_select) 
val_mca = val_mca.transform(X_val_cat_select)

test_mca = prince.MCA()
test_mca = test_mca.fit(X_test_cat_select) 
test_mca = test_mca.transform(X_test_cat_select)

train_mca.info()

val_mca.info()

train_mca.describe()

#Applying Max-Min scalling to the mca datasets, to have the same scale of the rest of the features.
for i in train_mca.columns:
    train_mca[i] = (train_mca[i] - train_mca[i].min()) / (train_mca[i].max() - train_mca[i].min())

for i in val_mca.columns:
    val_mca[i] = (val_mca[i] - val_mca[i].min()) / (val_mca[i].max() - val_mca[i].min())

for i in test_mca.columns:
    test_mca[i] = (test_mca[i] - test_mca[i].min()) / (test_mca[i].max() - test_mca[i].min())

#Renaming the MCA features to string values, through copying the feautures.
train_mca['MCA-1']=train_mca[0]
train_mca['MCA-2']=train_mca[1]
train_mca.drop(columns=[0,1], inplace=True)
val_mca['MCA-1']=val_mca[0]
val_mca['MCA-2']=val_mca[1]
val_mca.drop(columns=[0,1], inplace=True)
test_mca['MCA-1']=test_mca[0]
test_mca['MCA-2']=test_mca[1]
test_mca.drop(columns=[0,1], inplace=True)

train_mca.describe()

#The original X_train columns and the MCA components are concatenated, creating a dataset with all features.
train_all = pd.concat([X_train, train_mca], axis="columns")
val_all = pd.concat([X_val, val_mca], axis="columns")
test_all = pd.concat([X_test, test_mca], axis="columns")

"""Autoencoder feature generation"""

tf.random.set_seed(30)
np.random.seed(30)

n = 5
_, input_neurons = X_train.shape

encoder = keras.models.Sequential([
    keras.layers.Dense(n, input_shape=[input_neurons]),
])
decoder = keras.models.Sequential([
    keras.layers.Dense(input_neurons, input_shape=[n]),
])

Autoencoder = keras.models.Sequential([encoder, decoder])
Autoencoder.compile(
    loss="mse",
    optimizer=keras.optimizers.Adam(learning_rate=0.001)
)

print(Autoencoder.summary())

history = Autoencoder.fit(
    X_train, X_train, epochs=10,
    validation_data=(X_val, X_val)
)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.savefig(
    'Autoencoder_train_loss.jpg',
    bbox_inches='tight',
)
plt.show()

ae_train_feature_array = np.array(encoder.predict(X_train))
ae_val_feature_array = np.array(encoder.predict(X_val))
ae_test_feature_array = np.array(encoder.predict(X_test))

ae_train = create_new_features_dataframe(ae_train_feature_array , "ae")
ae_val = create_new_features_dataframe(ae_val_feature_array , "ae")
ae_test = create_new_features_dataframe(ae_test_feature_array , "ae")

ae_train.describe()

"""Therefore, there are 4 types of datasets, depending on the features:
X_train/val/test containing the created original dataset.
train/val/_mca, with the mca components.
train/val/_all, that included all original features + MCA components.
train/val_ae, with the Autoencoder features.

Summary of general information of all datasets created.
"""

X_train.info()

train_mca.info()

train_all.info()

ae_train.info()

"""**Experiments.**"""

#Function to generate evaluation metrics report.
def evaluate_results(y, y_pred):
  """
  Evaluation Metrics:
  - Accuracy (Acc)
  - Recall
  - False Alarm (FAR): FP / N
  - Type II Error: FN / (FN + TP)
  - F1
  - MCC
  """
  tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

  acc = accuracy_score(y, y_pred)
  recall = recall_score(y, y_pred)
  far = fp / (tn + fn)
  type_ii_err = fp / (fp + tn)
  f1 = f1_score(y, y_pred)
  mcc = matthews_corrcoef(y, y_pred)
  roc_auc = roc_auc_score(y, y_pred)

  print(f"Confussion Matrix:")
  print(f"\t{tp}\t{fn}")
  print(f"\t{fp}\t{tn}")

  print(f"Accuracy: {acc}")
  print(f"Detection Rate: {recall}")
  print(f"False Alarm Rate: {far}")
  print(f"Type II Error: {type_ii_err}")
  print(f"F1: {f1}")
  print(f"MCC: {mcc}")
  print(f"Roc auc: {roc_auc}")

  return dict(
      accuracy=acc,
      recall=recall,
      far=far,
      type_ii_err=type_ii_err,
      f1=f1,
      mcc=mcc,
      roc_auc=roc_auc,
  )

overall_results = [] #to reset the report list.

"""

Original features + Simple XGBoost Classifier
 """

hyperparams = dict(
  n_estimators=3,
  max_depth=3,
  random_state=30
)

performance = {}

performance["classifier"] = "Simple XGBoost"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = xgb.XGBClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(X_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}_overfited.jpg',
    bbox_inches='tight',
)

"""
 Original features + Linear booster XGBoost Classifier"""

hyperparams = dict(
  n_estimators=3,
  max_depth=3,
  booster='gblinear', 
  random_state=30
)

performance = {}

performance["classifier"] = "Linear XGBoost"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = xgb.XGBClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time


print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(X_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

""" MCA components + Simple XGBoost Classifier (as it seems to perform better than linear XGBoost)"""

hyperparams = dict(
  n_estimators=3,
  max_depth=3,
  random_state=30
)

performance = {}

performance["classifier"] = "XGBoost"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = xgb.XGBClassifier(**hyperparams)
time_to_process = time.time() - start_time


start_time = time.time()
model.fit(train_mca, y_train) 
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_mca));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(val_mca));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

""" MCA + original features + Simple XGBoost Classifier"""

hyperparams = dict(
  n_estimators=3,
  max_depth=3,
  random_state=30
)

performance = {}

performance["classifier"] = "XGBoost"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA + Original features"
performance["hyperparams"] =str(hyperparams)


start_time = time.time()
model = xgb.XGBClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(train_all, y_train) 
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_all)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(val_all)); 

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""MCA components + SVM classfier"""

start_time = time.time()
model = LinearSVC() 
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(train_mca, y_train) 
time_to_fit = time.time() - start_time

performance = {}

hyperparams = model.get_params()

performance["classifier"] = "SVM"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA"
performance["hyperparams"] =str(hyperparams)

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_mca)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(val_mca)); 

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Autoencoder features + Simple XGBoost Classifier"""

hyperparams = dict(
  n_estimators=3,
  max_depth=3,
  random_state=30
)

performance = {}

performance["classifier"] = "XGBoost"
performance["feature_gen"] = "Autoencoder"
performance["feature_sel"] = "Autoencoder"
performance["hyperparams"] =str(hyperparams)


start_time = time.time()
model = xgb.XGBClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(ae_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(ae_train));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(ae_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}_overfited.jpg',
    bbox_inches='tight',
)

"""Autoencoder + SVM classifier"""

start_time = time.time()
model = LinearSVC()
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(ae_train, y_train) 
time_to_fit = time.time() - start_time

performance = {}

hyperparams = model.get_params()

performance["classifier"] = "SVM"
performance["feature_gen"] = "Autoencoder"
performance["feature_sel"] = "Autoencoder"
performance["hyperparams"] =str(hyperparams)

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(ae_train));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(ae_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Original features + ANN (multi layer perceptron - MLP) classifier"""

hyperparams = dict(
      hidden_layer_sizes=(
          5,
      ),
      random_state=1
)

performance = {}

performance["classifier"] = "ANN"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)


start_time = time.time()
model = MLPClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(X_val)); 

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Autoencoder features + ANN (multi layer perceptron - MLP) classifier"""

hyperparams = dict(
      hidden_layer_sizes=(
          5,
      ),
      random_state=1
)

performance = {}

performance["classifier"] = "ANN"
performance["feature_gen"] = "Autoencoder"
performance["feature_sel"] = "Autoencoder"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = MLPClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(ae_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(ae_train)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(ae_val)); 

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Original features with Decision tree

"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30
)

performance = {}

performance["classifier"] = "Decision tree"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = DecisionTreeClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(X_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""MCA with Decision tree

"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30
)

performance = {}

performance["classifier"] = "Decision tree"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = DecisionTreeClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(train_mca, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_mca));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(val_mca));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""MCA + original features with Decision tree"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30
)

performance = {}

performance["classifier"] = "Decision tree"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA + Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = DecisionTreeClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(train_all, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_all));
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(val_all)); 

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Autoencoder features with Decision tree

"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30
)

performance = {}

performance["classifier"] = "Decision tree"
performance["feature_gen"] = "Autoencoder"
performance["feature_sel"] = "Autoencoder"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = DecisionTreeClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(ae_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(ae_train)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(ae_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Original features with Random Forest"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30)

performance = {}

performance["classifier"] = "Random Forest"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = RandomForestClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(X_val));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Original features + MCA with Random Forest"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30)

performance = {}

performance["classifier"] = "Random Forest"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA + Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = RandomForestClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(train_all, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_all)); 
print('\nVal Dataset\n')
performance['val'] = evaluate_results(y_val, model.predict(val_all));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

pd.concat(overall_results).loc["f1"].sort_values(by="val", ascending=False)

pd.concat(overall_results).loc["recall"].sort_values(by="val", ascending=False)

pd.concat(overall_results).loc["accuracy"].sort_values(by="val", ascending=False)

pd.concat(overall_results).loc["type_ii_err"].sort_values(by="val", ascending=False)

"""**Selected algorthims for testing**

Original features + Linear booster XGBoost Classifier
"""

hyperparams = dict(
  n_estimators=3,
  max_depth=3,
  booster='gblinear', 
  random_state=30
)

performance = {}

performance["classifier"] = "Linear XGBoost"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = xgb.XGBClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time


print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train));
print('\nTest Dataset\n')
performance['test'] = evaluate_results(y_test, model.predict(X_test));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Autoencoder + SVM classifier"""

start_time = time.time()
model = LinearSVC()
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(ae_train, y_train) 
time_to_fit = time.time() - start_time

performance = {}

hyperparams = model.get_params()

performance["classifier"] = "SVM"
performance["feature_gen"] = "Autoencoder"
performance["feature_sel"] = "Autoencoder"
performance["hyperparams"] =str(hyperparams)

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(ae_train));
print('\nTest Dataset\n')
performance['test'] = evaluate_results(y_test, model.predict(ae_test));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""MCA with Decision tree

"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30
)

performance = {}

performance["classifier"] = "Decision tree"
performance["feature_gen"] = "MCA"
performance["feature_sel"] = "MCA"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = DecisionTreeClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(train_mca, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(train_mca));
print('\nTest Dataset\n')
performance['test'] = evaluate_results(y_test, model.predict(test_mca));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)

"""Original features with Random Forest"""

hyperparams = dict(max_features = None,
                            max_depth = 45,
                            min_samples_split = 3,
                            min_samples_leaf = 30,
                            random_state=30)

performance = {}

performance["classifier"] = "Random Forest"
performance["feature_gen"] = ""
performance["feature_sel"] = "Original features"
performance["hyperparams"] =str(hyperparams)

start_time = time.time()
model = RandomForestClassifier(**hyperparams)
time_to_process = time.time() - start_time

start_time = time.time()
model.fit(X_train, y_train)
time_to_fit = time.time() - start_time

print('\nTrain Dataset\n')
performance['train'] = evaluate_results(y_train, model.predict(X_train)); 
print('\nTest Dataset\n')
performance['test'] = evaluate_results(y_test, model.predict(X_test));

summary = pd.DataFrame(performance)
overall_results.append(summary)

print('\nSUMMARY')
print(summary)
print(time_to_fit)
print(time_to_process)

sns.set(font_scale=1)
img = summary.plot.bar(subplots=False, grid=True)
img.figure.savefig(
    f'{performance["classifier"]}_{performance["feature_gen"]}_{performance["feature_sel"]}.jpg',
    bbox_inches='tight',
)
