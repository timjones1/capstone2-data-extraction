## Cambridge Spark Applied Data Science Capstone Part 2 - Employment Contract Information Extraction for Wavelength.law

The second capstone project that I completed for Wavelength.law involved exrtracting discrete scturcutred data from free text describing various aspects of employment contracts such as holiday entitlement and hours of work.

My project report is available [here](Capstone%202%20Project%20Report%20for%20Wavelength.law.pdf): 

### Installation requirements

Use wavelength_extract.yml to recreate conda environment used on this part of the capstone 

#### Package versions
Spacy v2.3.2 

en-core-web-sm spacy model

scikit-learn v 0.22

#### Notebooks and Comments

Notebooks prefixed by Wave 2 are the ones directly invovled in training of models and submissions. exploratory notebooks are not prefixed such as Matcher.ipynb and spacy experiments.ipynb

The main repository of code is in the wavefunctions.py. I wrote unit tests to test that rules based approaches were working as expected which saved alot of time cathcing bugs as my code became more complex, these are stored in the python files prefixed by test_wavelength...

The final trained Spacy model for test data is stored in the final model folder. The original training model is stored in the main part 2 folder.

 Final exports in xlsx form are saved in the exports folder and in the JSON folder when exporting for annotation.

