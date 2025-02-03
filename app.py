import streamlit as st
from lxml import etree
from pathlib import Path
from io import BytesIO
from collections import defaultdict

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def parse_xml(file_path):
    """Parses an XML file and returns the tree."""
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(str(file_path), parser)
        return tree
    except Exception as e:
        st.error(f"Error parsing XML file `{file_path.name}`: {e}")
        return None

def get_all_authors(parsed_trees):
    """Extracts all unique authors from the list of XML trees."""
    authors = set()
    for tree in parsed_trees:       
        # From bibliography
        bib_authors = tree.xpath('//tei:bibl/tei:author/tei:persName', namespaces=NS)
        for author in bib_authors:
            if author.text:
                authors.add(author.text.strip())
    return sorted(authors)

def get_all_keywords(parsed_trees):
    """Extracts all unique keywords from the list of XML trees."""
    keywords = set()
    for tree in parsed_trees:
        keyword_items = tree.xpath('//tei:keywords/tei:list/tei:item', namespaces=NS)
        for item in keyword_items:
            if item.text:                
                parts = [kw.strip() for kw in item.text.split(',')]
                keywords.update(parts)
    return sorted(keywords)

def get_all_place_names(parsed_trees):
    """Extracts all unique place names from the list of XML trees."""
    places = set()
    for tree in parsed_trees:       
        provenance_places = tree.xpath('//tei:provenance/tei:placeName', namespaces=NS)
        for place in provenance_places:
            if place.text and place.text.lower() != 'none':
                places.add(place.text.strip())        
        
        location_names = tree.xpath('//tei:location/tei:name[@type="place"]', namespaces=NS)
        for name in location_names:
            if name.text and name.text.lower() != 'none':
                places.add(name.text.strip())        
        
        contemporary_names = tree.xpath('//tei:div[@type="commentary"]//tei:name[@type="contemporary"]', namespaces=NS)
        for name in contemporary_names:
            if name.text and name.text.lower() != 'none':
                places.add(name.text.strip())        
        
        current_names = tree.xpath('//tei:name[@type="current"]', namespaces=NS)
        for name in current_names:
            if name.text and name.text.lower() != 'none':
                places.add(name.text.strip())
    return sorted(places)

def build_author_mappings(parsed_trees, xml_files):
    """
    Builds mappings from authors to their associated places and keywords.
    
    Returns:
        author_to_places (dict): Maps each author to a set of associated places.
        author_to_keywords (dict): Maps each author to a set of associated keywords.
    """
    author_to_places = defaultdict(set)
    author_to_keywords = defaultdict(set)
    
    for tree in parsed_trees:
        # Extract authors
        authors = set()        
        bib_authors = tree.xpath('//tei:bibl/tei:author/tei:persName', namespaces=NS)
        for author in bib_authors:
            if author.text:
                authors.add(author.text.strip())
        
        # Extract places
        places = set()
        provenance_places = tree.xpath('//tei:provenance/tei:placeName', namespaces=NS)
        for place in provenance_places:
            if place.text and place.text.lower() != 'none':
                places.add(place.text.strip())
        
        location_names = tree.xpath('//tei:location/tei:name[@type="place"]', namespaces=NS)
        for name in location_names:
            if name.text and name.text.lower() != 'none':
                places.add(name.text.strip())
        
        contemporary_names = tree.xpath('//tei:div[@type="commentary"]//tei:name[@type="contemporary"]', namespaces=NS)
        for name in contemporary_names:
            if name.text and name.text.lower() != 'none':
                places.add(name.text.strip())
        
        current_names = tree.xpath('//tei:name[@type="current"]', namespaces=NS)
        for name in current_names:
            if name.text and name.text.lower() != 'none':
                places.add(name.text.strip())        
        
        keywords = set()
        keyword_items = tree.xpath('//tei:keywords/tei:list/tei:item', namespaces=NS)
        for item in keyword_items:
            if item.text:
                parts = [kw.strip() for kw in item.text.split(',')]
                keywords.update(parts)        
       
        for author in authors:
            author_to_places[author].update(places)
            author_to_keywords[author].update(keywords)
    
    return author_to_places, author_to_keywords

def get_commentary(tree):
    """Extracts commentary sections from a single XML tree."""
    commentaries = tree.xpath('//tei:div[@type="commentary"]', namespaces=NS)
    commentary_list = []
    for comm in commentaries:
        subtype = comm.get('subtype', 'general')
        content = etree.tostring(comm, pretty_print=True, encoding='unicode')
        commentary_list.append({'subtype': subtype, 'content': content})
    return commentary_list

def get_editions(tree):
    """Extracts edition sections from a single XML tree."""
    editions = tree.xpath('//tei:div[@type="edition"]', namespaces=NS)
    edition_list = []
    for edition in editions:
        
        lang = edition.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')        
        content = etree.tostring(edition, pretty_print=True, encoding='unicode')
        edition_list.append({'lang': lang, 'content': content})
    return edition_list

def search_by_author(tree, author_query):
    """Searches for the author in titleStmt and bibliography."""
    results = []       
    
    bib_authors = tree.xpath('//tei:bibl/tei:author/tei:persName', namespaces=NS)
    for author in bib_authors:
        if author.text and author_query.lower() in author.text.lower():
            results.append(f"Bibliography Author: {author.text}")
    return results

def search_by_place(tree, place_query):
    """
    Searches for the place in provenance, contemporary names, and location geo elements.
    
    Parameters:
        tree (etree.Element): Parsed XML tree.
        place_query (str): The place name to search for.
    
    Returns:
        list: A list of strings describing where the place was found.
    """
    results = []
    place_query_lower = place_query.lower()    
   
    provenance_places = tree.xpath('//tei:provenance/tei:placeName', namespaces=NS)
    for place in provenance_places:
        if place.text and place_query_lower in place.text.lower() and place.text.lower() != "none":
            results.append(f"Provenance Place: {place.text.strip()}")
  
    contemporary_names = tree.xpath(
        '//tei:div[@type="commentary" and @subtype="general"]//tei:name[@type="contemporary"]',
        namespaces=NS
    )
    for name in contemporary_names:
        if name.text and place_query_lower in name.text.lower():
            results.append(f"Contemporary Name: {name.text.strip()}")    
   
    geo_elements = tree.xpath('//tei:location//tei:geo', namespaces=NS)
    for geo in geo_elements:
        if geo.text and place_query_lower in geo.text.lower() and geo.text.lower() != "none":
            results.append(f"Location Geo: {geo.text.strip()}")
    
    return results

def search_by_keyword(tree, keyword):
    """Searches for the keyword in keywords and commentary segments."""
    results = []   
    keyword_items = tree.xpath('//tei:keywords/tei:list/tei:item', namespaces=NS)
    for item in keyword_items:
        if item.text and keyword.lower() in item.text.lower():
            results.append(f"Keyword: {item.text}")    
    commentary_segs = tree.xpath('//tei:div[@type="commentary"]//tei:seg', namespaces=NS)
    for seg in commentary_segs:
        if seg.text and keyword.lower() in seg.text.lower():
            results.append(f"Commentary Segment: {seg.text}")
    return results

def display_tei_header(tree):
    title = tree.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', namespaces=NS)
    author = tree.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author/tei:persName', namespaces=NS)
    publication = tree.xpath('//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:publisher', namespaces=NS)
    date = tree.xpath('//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date', namespaces=NS)

    if title:
        st.write(f"**Title:** {title[0].text}")
    if author:
        st.write(f"**Author:** {author[0].text}")
    if publication:
        st.write(f"**Publisher:** {publication[0].text}")
    if date:
        st.write(f"**Date:** {date[0].text}")

def display_code_wrapped(content):
    """
    Custom function to display code with wrapping using st.markdown and HTML.
    This avoids horizontal scrolling by wrapping long lines.
    """
    st.markdown(
        f"""
        <div style="white-space: pre-wrap; word-wrap: break-word; font-size:14px; background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: hidden;">
            <code>{content}</code>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():    
    st.set_page_config(page_title="DigitalSEE TEI XML Viewer", layout="wide")   
   
    st.markdown(
        """
        <style>
        /* Enable code wrapping in st.code blocks */
        pre, code {
            white-space: pre-wrap !important; /* Allows wrapping */
            word-wrap: break-word !important;  /* Breaks long words */
            overflow-x: hidden !important;     /* Hides horizontal scrollbar */
        }
        /* Adjust font size for better fit */
        .streamlit-expanderHeader, pre, code {
            font-size: 14px !important;
        }
        /* Ensure the container doesn't force a minimum width */
        .streamlit-expander, .block-container {
            max-width: 100% !important;
        }
        /* Optional: Style for the code background */
        pre {
            background-color: #f5f5f5 !important;
            padding: 10px !important;
            border-radius: 5px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📄 DigitalSEE TEI XML Viewer")

    
    xml_folder = Path("./xmls")  

    if not xml_folder.exists() or not xml_folder.is_dir():
        st.error(f"The specified folder `{xml_folder}` does not exist or is not a directory.")
        st.stop()

    xml_files = list(xml_folder.glob("*.xml"))
    if not xml_files:
        st.info(f"No XML files found in the folder `{xml_folder}`.")
        st.stop()

    st.sidebar.header("📂 XML Files Overview")
    st.sidebar.write(f"**Total XML Files Loaded:** {len(xml_files)}")

    parsed_trees = []
    valid_files = []
    for file in xml_files:
        tree = parse_xml(file)
        if tree is not None:
            parsed_trees.append(tree)
            valid_files.append(file)

    if not parsed_trees:
        st.error("No valid XML files were parsed successfully.")
        st.stop()

    all_authors = get_all_authors(parsed_trees)
    all_keywords = get_all_keywords(parsed_trees)
    all_place_names = get_all_place_names(parsed_trees)

    author_to_places, author_to_keywords = build_author_mappings(parsed_trees, valid_files)

    st.header("🔍 Search TEI XML Files")

    search_col1, search_col2, search_col3 = st.columns(3)

    with search_col1:
        st.markdown("**Search by Author**")
        selected_author = st.selectbox("Select Author", options=["-- Select Author --"] + all_authors, key="author_select")

    if selected_author != "-- Select Author --":
        filtered_places = sorted(author_to_places[selected_author])
        filtered_keywords = sorted(author_to_keywords[selected_author])
    else:
        filtered_places = all_place_names
        filtered_keywords = all_keywords

    with search_col2:
        st.markdown("**Search by Place Name**")
        selected_place = st.selectbox("Select Place", options=["-- Select Place --"] + filtered_places, key="place_select")

    with search_col3:
        st.markdown("**Search by Keyword**")
        selected_keyword = st.selectbox("Select Keyword", options=["-- Select Keyword --"] + filtered_keywords, key="keyword_select")

    
    if st.button("🔎 Search"):
        st.subheader("🔗 Search Results")

        matched_files = set(valid_files)  

        
        if selected_author != "-- Select Author --":
            author_matched = set()
            for tree, file in zip(parsed_trees, valid_files):
                if search_by_author(tree, selected_author):
                    author_matched.add(file)
            matched_files = matched_files.intersection(author_matched)
        
        
        if selected_place != "-- Select Place --":
            place_matched = set()
            for tree, file in zip(parsed_trees, valid_files):
                if search_by_place(tree, selected_place):
                    place_matched.add(file)
            matched_files = matched_files.intersection(place_matched)
        
        
        if selected_keyword != "-- Select Keyword --":
            keyword_matched = set()
            for tree, file in zip(parsed_trees, valid_files):
                if search_by_keyword(tree, selected_keyword):
                    keyword_matched.add(file)
            matched_files = matched_files.intersection(keyword_matched)        
        
        if matched_files:
            st.write(f"**Total Matches:** {len(matched_files)}")
            for file in matched_files:
                tree = parse_xml(file)  
                if tree is not None:
                    with st.expander(f"📄 {file.name}"):
                        display_tei_header(tree)
                        
                        commentaries = get_commentary(tree)
                        if commentaries:
                            st.markdown("**Commentary Sections:**")
                            for idx, comm in enumerate(commentaries, start=1):
                                st.markdown(f"**Commentary {idx} - {comm['subtype']}**")
                                st.code(comm['content'], language='xml')
                              
                        else:
                            st.write("No commentary sections found.")

                        editions = get_editions(tree)
                        if editions:
                            st.markdown("**Edition Sections:**")
                            for idx, edition in enumerate(editions, start=1):
                                st.markdown(f"**Edition {idx} - Language: {edition['lang']}**")
                                st.code(edition['content'], language='xml')
                                
                        else:
                            st.write("No edition sections found.")

                        associated_places = sorted(author_to_places.get(selected_author, set())) if selected_author != "-- Select Author --" else sorted(get_all_place_names([tree]))
                        associated_keywords = sorted(author_to_keywords.get(selected_author, set())) if selected_author != "-- Select Author --" else sorted(get_all_keywords([tree]))

                        if associated_places:
                            st.markdown("**Associated Places:**")
                            st.write(", ".join(associated_places))
                        if associated_keywords:
                            st.markdown("**Associated Keywords:**")
                            st.write(", ".join(associated_keywords))

                        
                        buffer = BytesIO()
                        tree.write(buffer, pretty_print=True, encoding='utf-8', xml_declaration=True)
                        buffer.seek(0)
                        st.download_button(
                            label="📥 Download XML",
                            data=buffer,
                            file_name=f"matched_{file.name}",
                            mime="application/xml"
                        )
        else:
            st.write("No matching files found for the given search criteria.")

    with st.expander("📚 View All Loaded XML Files"):
        for tree, file in zip(parsed_trees, valid_files):
            with st.container():
                st.markdown(f"### 📄 {file.name}")
                display_tei_header(tree)

                commentaries = get_commentary(tree)
                if commentaries:
                    st.markdown("**Commentary Sections:**")
                    for idx, comm in enumerate(commentaries, start=1):
                        st.markdown(f"**Commentary {idx} - {comm['subtype']}**")
                        st.code(comm['content'], language='xml')
              
                else:
                    st.write("No commentary sections found.")

                editions = get_editions(tree)
                if editions:
                    st.markdown("**Edition Sections:**")
                    for idx, edition in enumerate(editions, start=1):
                        st.markdown(f"**Edition {idx} - Language: {edition['lang']}**")
                        st.code(edition['content'], language='xml')
                       
                else:
                    st.write("No edition sections found.")

    st.sidebar.markdown("---")      
    st.sidebar.header("Simple Querying Interface")
    st.sidebar.write(
        "Quickly search and filter TEI XML files to find relevant information or themes."
    )

    st.sidebar.header("XML Code Viewer")
    st.sidebar.write(
        "View detailed XML code for commentaries and editions in their original format."
    )

    st.sidebar.header("Downloadable Entries")
    st.sidebar.write(
        "Download entries for offline access and further analysis."
    )

    st.sidebar.header("Comprehensive Meta Information")
    st.sidebar.write(
        "Each entry includes rich metadata, such as XML file author details."
    )

  

if __name__ == "__main__":
    main()
