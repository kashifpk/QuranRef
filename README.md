# QuranRef

Online and embeddable Quran Reference. Currently contains:

* Uthmani arabic text
* Urudu translation (Maududi)
* English Translation (Maududi)

(Quran texts and translations provided by  `The Tanzil Project <http://tanzil.net>`_)

## Development Getting Started


### 1. Create a python virtual environment

```shell
python3 -m venv venv
source venv/bin/activate
```

### 2. Clone the repo and set it up in development mode.

```shell
git clone git@github.com:kashifpk/QuranRef.git
cd Quranref

python setup.py develop
```

### 3. Install ArangoDB

Install arangodb3 and then create a database with these credentials (also present in development.ini)

DB: quranref
username: kashif
password: compulife

### 4. Create database collections, graphs and import data


```shell
quranref_populate development.ini
quranref_import_surah_info development.ini

# Import arabic text and translations. Feel free to add more translations and arabic text present in the data folder. Example:

quranref_import_text development.ini arabic uthmani data/quran-uthmani.txt
quranref_import_text development.ini urdu maududi data/translations/ur.maududi.txt
quranref_import_text development.ini english maududi data/translations/ur.maududi.txt
```


### 5. Run Backend API

```shell
pserve --reload development.ini
```

### 6. Run Frontend (In a separate terminal)

Make sure you have npm installed.

```shell
cd quranref-frontend
npm install
npm run dev
```
