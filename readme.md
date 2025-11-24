# Utrecht Sport Accomodation Availability checker

This tool will gather the availabily diagrams from the utrecht sport accomodaties endpoint and display them in a single graph, which will make it easier to search for an appropriate accomodation

## Setup
Create a copy of the `template.json` file and fill the required fields. You'll find the hall_ids on the Utrecht Sportaccomodaties website, for instance:
[https://asp5.lvp.nl/amisweb/utrecht/amis1/amis.php?action=objinfo&obj_id=1000003152](https://asp5.lvp.nl/amisweb/utrecht/amis1/amis.php?action=objinfo&obj_id=1000003152) 

Where the `obj_id` param is the value that needs to be taken.
Dates are written in Year, Month, Day format (4, 2 and 2 digits respectively). Day of the week is denoted by the three letter abbreviation (in lower caps), like `mon` for thursday.

You might need to install some packages. It's recommended to use a virtual env (for instance venv) or another tool. You'll find the requirement list in `requirements.txt` which can be installed like so:

```bash
pip install -r requirements.txt
```

## Running
Now that you have created a configuration you can run the project using the following command:

```bash
py main.py configs/my_new_config.json
```

the `--no-fetch` option can be used to not refetch the latest information from the *'api'*. This option is disabled by default.

You will find the resulting graph in the img folder.
