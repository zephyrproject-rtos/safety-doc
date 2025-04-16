import os
import xml.etree.ElementTree as ET
import argparse

def parse_doxygen_xml(xml_file):
    """
    Parse the Doxygen XML file and extract test functions.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract all memberdef elements with kind="function"
    test_functions = []
    for memberdef in root.findall(".//memberdef[@kind='function']"):
        function_name = memberdef.find("name").text
        if function_name.startswith("test_"):
            location = memberdef.find("location").attrib
            file_path = location.get("file")
            line_number = location.get("line")
            test_functions.append((function_name, file_path, line_number))

    return test_functions

def find_inner_groups(xml_file):
    """
    Parse the XML file to find all innergroup references.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract all innergroup elements
    inner_groups = []
    for innergroup in root.findall(".//innergroup"):
        refid = innergroup.attrib.get("refid")
        if refid:
            inner_groups.append(refid)

    return inner_groups

def list_all_tests(starting_xml, xml_dir):
    """
    Recursively list all test functions starting from the given XML file.
    """
    # Parse the starting XML file for inner groups
    inner_groups = find_inner_groups(starting_xml)

    # Initialize a list to store all test functions
    all_test_functions = []

    # Traverse each inner group
    for group in inner_groups:
        group_file = os.path.join(xml_dir, f"{group}.xml")
        if os.path.exists(group_file):
            # Parse the group XML file for test functions
            test_functions = parse_doxygen_xml(group_file)
            all_test_functions.extend(test_functions)
        else:
            print(f"Warning: Referenced group file {group_file} does not exist.")

    # Print all test functions
    print("List of all test functions:")
    for func, file, line in all_test_functions:
        print(f"{func} - {file}:{line}")

def parse_group_description(xml_file):
    """
    Parse the group XML file to extract the group description and test functions.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract the group title (description)
    title = root.find(".//title").text if root.find(".//title") is not None else "No Title"

    # Extract all memberdef elements with kind="function"
    test_functions = []
    for memberdef in root.findall(".//memberdef[@kind='function']"):
        function_name = memberdef.find("name").text
        if not function_name.startswith("test_"):
            continue
        brief_description = ""
        brief_para = memberdef.find("briefdescription/para")
        if brief_para is not None:
            for element in brief_para.iter():
                if element.tag == "ref":
                    brief_description += f":c:func:`{element.text.strip('\n')}`"  or ""                   
                elif element.text:
                    brief_description += element.text.strip('\n')             
                if element.tail:
                    brief_description += element.tail.strip('\n') or ""
                
        brief_description = brief_description.strip() if brief_description else "No description"

        # Check for requirements validated by the test
        validates = []
        for xrefsect in memberdef.findall(".//xrefsect"):
            xreftitle = xrefsect.find("xreftitle")
            if xreftitle is not None and xreftitle.text == "Verifies requirement":
                for ref in xrefsect.findall(".//ref"):
                    validates.append(ref.text)

        test_functions.append((function_name, brief_description, validates))

    return title, test_functions

def generate_rst_file(group_id, group_title, test_functions, output_dir):
    """
    Generate an RST file for a group with its tests.
    """
    rst_file_path = os.path.join(output_dir, f"{group_id}.rst")
    with open(rst_file_path, "w") as rst_file:
        # Write the group title as the header
        rst_file.write(f"{group_title}\n")
        rst_file.write(f"{'=' * len(group_title)}\n\n")

        # Write each test in the specified format
        for function_name, brief_description, validates in test_functions:
            rst_file.write(f".. item:: {function_name}\n")
            if validates:
                rst_file.write(f"    :validates: {' '.join(validates)}\n")
            rst_file.write("\n")
            rst_file.write(f"    {brief_description}\n")
            rst_file.write("\n")
            rst_file.write(f"    :c:func:`{function_name}()`\n\n")

    print(f"Generated RST file: {rst_file_path}")

def process_groups(starting_xml, xml_dir, output_dir):
    """
    Process all groups starting from the given XML file and generate RST files.
    """
    # Parse the starting XML file for inner groups
    tree = ET.parse(starting_xml)
    root = tree.getroot()
    inner_groups = [innergroup.attrib.get("refid") for innergroup in root.findall(".//innergroup")]

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each group
    for group_id in inner_groups:
        group_file = os.path.join(xml_dir, f"{group_id}.xml")
        if os.path.exists(group_file):
            group_title, test_functions = parse_group_description(group_file)
            generate_rst_file(group_id, group_title, test_functions, output_dir)
        else:
            print(f"Warning: Referenced group file {group_file} does not exist.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RST files for each group from Doxygen XML files.")
    parser.add_argument("--input", required=True, help="Path to the starting XML file (e.g., group__all__tests.xml).")
    parser.add_argument("--xml-dir", required=True, help="Directory containing all Doxygen XML files.")
    parser.add_argument("--output-dir", required=True, help="Directory to save the generated RST files.")

    args = parser.parse_args()

    starting_xml = args.input
    xml_dir = args.xml_dir
    output_dir = args.output_dir

    if not os.path.exists(starting_xml):
        print(f"Error: Starting XML file {starting_xml} does not exist.")
    elif not os.path.isdir(xml_dir):
        print(f"Error: XML directory {xml_dir} does not exist.")
    else:
        process_groups(starting_xml, xml_dir, output_dir)