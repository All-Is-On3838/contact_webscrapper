import pandas as pd
import csv
import logging

#set logger
logger = logging.getLogger(__name__) 
logger.setLevel(logging.DEBUG) 

def csv_to_dict(csv_file):
    result = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            result.append(row)
    return result


def format_update(master_item, data_item, column):
    status = {}
    try:
        try:
            master_set = set(eval(master_item[column]))
        except:
            master_set = set(master_item[column])
    except Exception as e:
        logger.exception(f"Error turning master_item into set for site: {master_item['site']}, {column}: {master_item[column]}. Error:", str(e))  
    data_set = set(data_item[column])
    check_set = master_set - data_set

    try:
        if check_set:
            status = {
                "site": master_item["site"],
                "note": f"{column} changed",
                f"old {column}": master_item[column],
                f"new {column}": data_item[column]
            }
    except Exception as e:
        logger.exception(f"Error formatting update for site: {data_item['site']}, {column}: {data_item[column]}. Error:", str(e))

    return status

def check_changes(master_item, data_item, column, result):
    try:
        returned = format_update(master_item, data_item, column)
    except Exception as e:
        logger.exception(f"Issue calling format_updates from check_changes. Error:", str(e))
    
    try:
        if returned: # Append if not empty
            result.append(returned)
    except Exception as e:
        logger.exception(f"Issue appending returned to result in check_changes. Error:", str(e))

def compare_files(masterfile, data, column_values, result):
    try:
        for master_item in masterfile:
            found = False
            for data_item in data:
                try:
                    if master_item["site"] == data_item["site"]:
                        found = True
                        for column in column_values:
                            check_changes(master_item, data_item, column, result)
                        break
                except KeyError as e:
                    logger.error(f"KeyError: {e} occurred in data_item")
                    # Handle the exception or perform any necessary actions

            if not found:
                result.append({
                    "site": master_item["site"],
                    "note": "site removed"
                })
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def check_new_sites(masterfile, data, column_values, result):
    try:
        for data_item in data:
            found = False
            for master_item in masterfile:
                if data_item["site"] == master_item["site"]:
                    found = True
                    break

            if not found:
                new_item = {
                    "site": data_item["site"],
                    "note": "site new",
                }
                for column in column_values:
                    new_item[column] = data_item[column]
                result.append(new_item)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def update_masterfile(masterfile, result):
    try:
        for updated in result:
            split = str.split(updated['note'])
            if split[1] == 'changed':
                found = False
                for i, master_item in enumerate(masterfile):
                    if updated["site"] == master_item["site"]:
                        found = True
                        masterfile[i][split[0]] = updated[f'new {split[0]}']
                        break

                if not found:
                    logger.error(f"Error while changing {split[0]} for {updated['site']}: unable to find site")

            elif split[1] == 'removed':
                found = False
                for i, master_item in enumerate(masterfile):
                    if updated["site"] == master_item["site"]:
                        found = True
                        masterfile.pop(i)
                        break

                if not found:
                    logger.error(f"Error while removing {split[0]} for {updated['site']}: unable to find site")
            elif split[1] == 'new':
                updated.pop('note')
                masterfile.append(updated)

            else:
                logger.error("status not considered")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def dict_to_csv(masterfile, file_name):
    # Convert dictionary to dataframe
    try:
        df = pd.DataFrame.from_dict(masterfile)
    except Exception as e:
        logger.exception("Unable convert dictionary to dataframe:", str(e))

    # Convert dataframe to csv
    file_path = file_name # Overwrite master file for comparison
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        logger.exception("Unable convert dataframe to csv:", str(e))


