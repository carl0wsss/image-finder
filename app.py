import streamlit as st
import requests
from dotenv import load_dotenv
import os

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

def search_pexels(query, page, orientation):
    orientations = {"Landscape": "landscape", "Portrait": "portrait", "Square": "square"}
    params = {"query": query, "per_page": PHOTOS_PAR_SOURCE, "page": page}
    if orientation != "ALL":
        params["orientation"] = orientations[orientation]
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

def search_pixabay(query, page, orientation, tri):
    orientations = {"Landscape": "horizontal", "Portrait": "vertical"}
    tris = {"Recent": "latest", "Popular": "popular"}
    params = {"key": PIXABAY_KEY, "q": query, "per_page": PHOTOS_PAR_SOURCE, "page": page, "image_type": "photo", "order": tris[tri]}
    if orientation in orientations:
        params["orientation"] = orientations[orientation]
    response = requests.get("https://pixabay.com/api/", params=params)
    data = response.json()
    total = data.get("totalHits", 0)
    total_pages = (total // PHOTOS_PAR_SOURCE) + 1
    photos = [{"url": p["webformatURL"], "link": p["pageURL"], "source": "Pixabay"} for p in data["hits"]]
    return photos, total_pages

st.title("Image Finder — CNBC Mongolia")

query = st.text_input("Put the keyword", placeholder='Search......')

st.sidebar.title("Menu")

PHOTOS_PAR_SOURCE = st.sidebar.selectbox(
    "Photos per source",
    [9, 18, 27],
    index=0
)

source_filtre = st.sidebar.multiselect(
    "Websites",
    ["Unsplash", "Pexels", "Pixabay"],
    default=["Unsplash", "Pexels", "Pixabay"]
)

orientation_filtre = st.sidebar.selectbox(
    "Format",
    ["ALL", "Landscape", "Portrait", "Square"]
)

couleur_filtre = None
if source_filtre == ["Unsplash"]:
    couleur_filtre = st.sidebar.selectbox(
        "Main color (Unsplash only)",
        ["ALL", "Black", "White", "Yellow", "Blue", "Orange", "Red", "Purple", "Green"]
    )

tri_filtre = "Popular"
if "Pexels" not in source_filtre:
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
        pexels_photos, pexels_pages = search_pexels(query, st.session_state.page, orientation_filtre)
        images += pexels_photos
        pages_actives.append(pexels_pages)
    if "Pixabay" in source_filtre:
        pixabay_photos, pixabay_pages = search_pixabay(query, st.session_state.page, orientation_filtre, tri_filtre)
        images += pixabay_photos
        pages_actives.append(pixabay_pages)

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

# Ajouter d'autres sites
# Creer des options taille et qualité
