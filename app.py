import streamlit as st
import requests
import os

try:
    UNSPLASH_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_ACCESS_KEY"]
    PIXABAY_KEY = st.secrets["PIXABAY_ACCESS_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    PEXELS_KEY = os.getenv("PEXELS_ACCESS_KEY")
    PIXABAY_KEY = os.getenv("PIXABAY_ACCESS_KEY")

PHOTOS_PAR_SOURCE = 9

def search_unsplash(query, page, orientation, couleur, tri):
    orientations = {"Landscape": "landscape", "Portrait": "portrait", "Square": "squarish"}
    tris = {"Recent": "latest", "Popular": "relevant"}
    params = {"query": query, "per_page": PHOTOS_PAR_SOURCE, "page": page, "order_by": tris[tri]}
    if orientation != "ALL":
        params["orientation"] = orientations[orientation]
    if couleur and couleur != "ALL":
        params["color"] = couleur.lower()
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        params=params,
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    )
    data = response.json()
    total_pages = data.get("total_pages", 1)
    photos = [{"url": p["urls"]["small"], "link": p["links"]["html"], "source": "Unsplash"} for p in data["results"]]
    return photos, total_pages

def search_pexels(query, page, orientation, taille):
    orientations = {"Landscape": "landscape", "Portrait": "portrait", "Square": "square"}
    tailles = {"Small": "small", "Medium": "medium", "Large": "large"}
    params = {"query": query, "per_page": PHOTOS_PAR_SOURCE, "page": page}
    if orientation != "ALL":
        params["orientation"] = orientations[orientation]
    if taille != "ALL":
        params["size"] = tailles[taille]
    response = requests.get(
        "https://api.pexels.com/v1/search",
        params=params,
        headers={"Authorization": PEXELS_KEY}
    )
    data = response.json()
    total = data.get("total_results", 0)
    total_pages = (total // PHOTOS_PAR_SOURCE) + 1
    photos = [{"url": p["src"]["medium"], "link": p["url"], "source": "Pexels"} for p in data["photos"]]
    return photos, total_pages

def search_pixabay(query, page, orientation, tri, taille):
    orientations = {"Landscape": "horizontal", "Portrait": "vertical"}
    tris = {"Recent": "latest", "Popular": "popular"}
    tailles_px = {
        "Small": {"min_width": 0, "max_width": 640},
        "Medium": {"min_width": 640, "max_width": 1920},
        "Large": {"min_width": 1920, "max_width": 7680}
    }
    params = {"key": PIXABAY_KEY, "q": query, "per_page": PHOTOS_PAR_SOURCE, "page": page, "image_type": "photo", "order": tris[tri]}
    if orientation in orientations:
        params["orientation"] = orientations[orientation]
    if taille != "ALL":
        params["min_width"] = tailles_px[taille]["min_width"]
        params["max_width"] = tailles_px[taille]["max_width"]
    response = requests.get("https://pixabay.com/api/", params=params)
    data = response.json()
    total = data.get("totalHits", 0)
    total_pages = (total // PHOTOS_PAR_SOURCE) + 1
    photos = [{"url": p["webformatURL"], "link": p["pageURL"], "source": "Pixabay"} for p in data["hits"]]
    return photos, total_pages

def search_openverse(query, page, orientation, taille):
    try:
        orientations = {"Landscape": "landscape", "Portrait": "portrait", "Square": "square"}
        tailles = {"Small": "small", "Medium": "medium", "Large": "large"}
        params = {"q": query, "page_size": PHOTOS_PAR_SOURCE, "page": page}
        if orientation != "ALL":
            params["aspect_ratio"] = orientations[orientation]
        if taille != "ALL":
            params["size"] = tailles[taille]
        response = requests.get("https://api.openverse.org/v1/images/", params=params)
        data = response.json()
        total = data.get("count", 0)
        total_pages = (total // PHOTOS_PAR_SOURCE) + 1
        results = data.get("results", [])
        photos = [{"url": p["thumbnail"], "link": p["foreign_landing_url"], "source": "Openverse"} for p in results if p.get("thumbnail")]
        return photos, total_pages
    except:
        return [], 1

def search_wikimedia(query, page):
    try:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": 6,
            "gsrlimit": PHOTOS_PAR_SOURCE,
            "gsroffset": (page - 1) * PHOTOS_PAR_SOURCE,
            "prop": "imageinfo",
            "iiprop": "url|thumburl",
            "iiurlwidth": 400,
            "format": "json",
            "origin": "*"
        }
        response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "CNBC-Mongolia-ImageFinder/1.0"}
        )
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        photos = []
        for p in pages.values():
            imageinfo = p.get("imageinfo", [{}])[0]
            thumb = imageinfo.get("thumburl", "")
            url = imageinfo.get("url", "")
            if thumb:
                photos.append({"url": thumb, "link": url, "source": "Wikimedia"})
        return photos, 50
    except:
        return [], 1

st.sidebar.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding-bottom:1rem; border-bottom:0.5px solid rgba(255,255,255,0.15); margin-bottom:0.5rem;">
        <div style="width:36px; height:36px; background:#4a90d9; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:10px; color:white; font-weight:500; text-align:center; line-height:1.2;">CNBC<br>MNG</div>
        <div>
            <div style="font-size:13px; font-weight:500; color:white;">Image Finder</div>
            <div style="font-size:10px; color:rgba(255,255,255,0.5);">CNBC Mongolia</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.title("Image Finder — CNBC Mongolia")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0a1f5c;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label {
            color: rgba(255,255,255,0.5) !important;
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
            background-color: rgba(255,255,255,0.08) !important;
            border-color: rgba(255,255,255,0.2) !important;
            color: white !important;
        }
        [data-testid="stSidebar"] span[data-baseweb="tag"] {
            background-color: #4a90d9 !important;
        }
        .stApp {
            background-color: #0f0f1a;
        }
        h1 {
            color: white !important;
        }
        .stTextInput input {
            background-color: rgba(255,255,255,0.06) !important;
            border-color: rgba(255,255,255,0.15) !important;
            color: white !important;
        }
        .stButton > button {
            background-color: #4a90d9 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
        }
        .stButton > button:hover {
            background-color: #2d7dd2 !important;
        }
        .streamlit-expanderHeader {
            color: #4a90d9 !important;
            font-size: 12px !important;
        }
        p {
            color: rgba(255,255,255,0.5) !important;
        }
    </style>
""", unsafe_allow_html=True)

query = st.text_input("Put the keyword", placeholder='Search......')

st.sidebar.title("Menu")

PHOTOS_PAR_SOURCE = st.sidebar.selectbox(
    "Photos per source",
    [9, 18, 27],
    index=0
)

source_filtre = st.sidebar.multiselect(
    "Websites",
    ["Unsplash", "Pexels", "Pixabay", "Openverse", "Wikimedia"],
    default=["Unsplash", "Pexels", "Pixabay", "Openverse", "Wikimedia"]
)

orientation_filtre = st.sidebar.selectbox(
    "Format",
    ["ALL", "Landscape", "Portrait", "Square"]
)

taille_filtre = st.sidebar.selectbox(
    "Size (Pexels, Pixabay and Openverse only)",
    ["ALL", "Small", "Medium", "Large"]
)

couleur_filtre = st.sidebar.selectbox(
    "Main color (Unsplash only)",
    ["ALL", "Black", "White", "Yellow", "Blue", "Orange", "Red", "Purple", "Green"]
)

tri_filtre = st.sidebar.selectbox(
    "Sort by (Unsplash and Pixabay only)",
    ["Popular", "Recent"]
)

if source_filtre != st.session_state.get("derniere_source"):
    st.session_state.page = 1
    st.session_state.derniere_source = source_filtre

if query:
    if "page" not in st.session_state:
        st.session_state.page = 1

    images = []
    pages_actives = []

    if "Unsplash" in source_filtre:
        unsplash_photos, unsplash_pages = search_unsplash(query, st.session_state.page, orientation_filtre, couleur_filtre, tri_filtre)
        images += unsplash_photos
        pages_actives.append(unsplash_pages)
    if "Pexels" in source_filtre:
        pexels_photos, pexels_pages = search_pexels(query, st.session_state.page, orientation_filtre, taille_filtre)
        images += pexels_photos
        pages_actives.append(pexels_pages)
    if "Pixabay" in source_filtre:
        pixabay_photos, pixabay_pages = search_pixabay(query, st.session_state.page, orientation_filtre, tri_filtre, taille_filtre)
        images += pixabay_photos
        pages_actives.append(pixabay_pages)
    if "Openverse" in source_filtre:
        openverse_photos, openverse_pages = search_openverse(query, st.session_state.page, orientation_filtre, taille_filtre)
        images += openverse_photos
        pages_actives.append(openverse_pages)
    if "Wikimedia" in source_filtre:
        wikimedia_photos, wikimedia_pages = search_wikimedia(query, st.session_state.page)
        images += wikimedia_photos
        pages_actives.append(wikimedia_pages)

    total_pages = min(max(pages_actives) if pages_actives else 1, 50)

    cols = st.columns(3)
    for i, photo in enumerate(images):
        with cols[i % 3]:
            st.image(photo["url"])
            with st.expander("URL"):
                st.write(photo["link"])

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.page > 1:
            if st.button("← Previous"):
                st.session_state.page -= 1
                st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center'>Page {st.session_state.page} of {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.session_state.page < total_pages:
            if st.button("Next →"):
                st.session_state.page += 1
                st.rerun()