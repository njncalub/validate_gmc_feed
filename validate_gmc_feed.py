#!/usr/bin/python

import csv
import datetime
import sys
import logging
from collections import Counter
from xml.etree import ElementTree as ET

TAXONOMY_FILE_PATH = "taxonomy_20150219.txt"
TAXONOMY_IDS_FILE_PATH = "taxonomy_with_ids_20150219.txt"
NOTFOUND_REPORT_FILE_PATH = "notfound_{timestamp}.csv"
FOUND_REPORT_FILE_PATH = "found_{timestamp}.csv"
ITEM_FOUND = "Found '{item}': {count}"
ITEM_NOT_FOUND = "Did not find '{item}': {count}"
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
PRODUCT_CATEGORY = {
    "ns": "http://base.google.com/ns/1.0",
    "attr": "google_product_category",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

GMC_XML_FILE_PATH = "feed_to_validate.xml"  # replace this


def load_taxonomy_file(path=TAXONOMY_FILE_PATH, mode="r", with_ids=False):
    """Loads the taxonomy file from a file.
    
    :param path: path of the file to be loaded.
    :param mode: mode to open the file
    :type path: string
    :type mode: string
    :return: returns a set for all the valid categories.
    :rtype: set
    """
    
    with open(path, mode) as tf:
        if with_ids:
            return {line.split()[0] for line in tf}
        else:
            return {line.strip() for line in tf}


def generate_csv(path, items=None, header=None, mode="wb"):
    """Generates a report using the CSV file format.
    
    :param path: path of the csv file to be created
    :param items: rows to write to the csv file
    :param header: first row to be written on the csv file
    :param mode: mode to open the file
    :type path: string
    :type items: iterable
    :type header: sequence
    :type mode: string
    :return: None
    :rtype: None
    """
    
    with open(path, mode) as csv_file:
        csv_writer = csv.writer(csv_file)
        
        if header:
            csv_writer.writerow(header)
        
        for item in items:
            csv_writer.writerow(item)
    
    logging.info("Generated '{}'.".format(path))


def main():
    """Load the required files and generate the report."""
    
    valid_categories = load_taxonomy_file(
        path=TAXONOMY_IDS_FILE_PATH,
        with_ids=True)
    
    tree = ET.parse(GMC_XML_FILE_PATH)
    categories = tree.findall(".//{{{ns}}}{attr}".format(**PRODUCT_CATEGORY))
    logging.info("Total items: {}".format(len(categories)))
    
    all_categories = Counter(c.text.strip() for c in categories)
    items_found = Counter()
    items_not_found = Counter()
    
    for item, count in all_categories.most_common():
        if item in valid_categories:
            items_found[item] = count
            logging.debug(ITEM_FOUND.format(item=item, count=count))
        else:
            items_not_found[item] = count
            logging.debug(ITEM_NOT_FOUND.format(item=item, count=count))
    
    len_all = len(all_categories)
    len_valid = len(items_found)
    len_invalid = len(items_not_found)
    logging.info("All categories: {}".format(len_all))
    logging.info("Valid categories: {} ({:.2f}%)".format(
        len_valid,
        (float(len_valid) / float(len_all)) * 100.0))
    logging.info("Invalid categories: {} ({:.2f}%)".format(
        len_invalid,
        (float(len_invalid) / float(len_all)) * 100.0))
    
    timestamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    generate_csv(
        path=NOTFOUND_REPORT_FILE_PATH.format(timestamp=timestamp),
        # items=sorted(items_not_found.iteritems(), key=lambda x: x[0].lower()),
        items=sorted(items_not_found.iteritems(), key=lambda x: int(x[0])),
        header=["Invalid Category", "Total"]
    )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
