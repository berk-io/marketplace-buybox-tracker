"""
Marketplace Buybox Tracker - Advanced UI Dashboard

This module provides a secure, streamlined web interface. It removes
the cumbersome sidebar in favor of a clean, tab-based navigation system,
retains the native theme toggles, parses URLs for automated product naming,
prevents duplicate entries, and includes dynamic search filtering.
"""

import streamlit as st
import json
import os
import time

# --- Page Configuration ---
st.set_page_config(page_title="PazarYeri Asistanı B2B", page_icon="🛒", layout="centered")

# --- File Paths ---
PRODUCTS_FILE = "products.json"
PROFILE_FILE = "profile.json"

# --- Helper Functions ---
def load_json(filepath):
    if not os.path.exists(filepath):
        return [] if filepath == PRODUCTS_FILE else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return [] if filepath == PRODUCTS_FILE else {}

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_product_name(url):
    """Trendyol linkinin içinden ürünün adını temiz bir şekilde çeker."""
    try:
        parts = url.split('/')
        if len(parts) > 4:
            name_slug = parts[4].split('-p-')[0]
            clean_name = name_slug.replace('-', ' ').title()
            return clean_name[:40] + "..." if len(clean_name) > 40 else clean_name
    except:
        pass
    return "Tanımsız Ürün"

# --- Session State Management ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 1. LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🔐 PazarYeri Asistanı")
    st.markdown("Lütfen yönetim paneline erişmek için giriş yapın.")
    
    with st.form("login_form"):
        email = st.text_input("E-posta Adresi", placeholder="admin@admin.com")
        password = st.text_input("Şifre", type="password")
        submit_login = st.form_submit_button("Giriş Yap")
        
        if submit_login:
            if email == "admin@admin.com" and password == "Tarsus2026!":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Hatalı e-posta veya şifre!")

# --- 2. MAIN DASHBOARD ---
if st.session_state.logged_in:
    
    # Header & Logout
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("🛒 Rakip Asistanı")
    with col2:
        st.write("") 
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # Load Data
    profile_data = load_json(PROFILE_FILE)
    products_data = load_json(PRODUCTS_FILE)

    # --- TABS (Sekmeler) ---
    tab1, tab2 = st.tabs(["📦 Ürün Yönetimi", "⚙️ Mağaza ve Profil"])

    # --- TAB 2: PROFILE SETTINGS ---
    with tab2:
        st.subheader("Mağaza Profil Ayarları")
        st.info("Bu bilgileri bir kere doldurmanız yeterlidir.")
        
        with st.form("profile_form"):
            store_name = st.text_input("Mağaza Adı", value=profile_data.get("store_name", ""))
            chat_id = st.text_input("Telegram Chat ID", value=profile_data.get("chat_id", ""))
            save_profile = st.form_submit_button("Ayarları Kaydet")
            
            if save_profile:
                if store_name and chat_id:
                    new_profile = {"store_name": store_name, "chat_id": chat_id}
                    save_json(PROFILE_FILE, new_profile)
                    st.toast("✅ Profil güncellendi!", icon="🎉")
                    profile_data = new_profile
                else:
                    st.error("Alanlar boş bırakılamaz.")

    # --- TAB 1: PRODUCT MANAGEMENT ---
    with tab1:
        with st.expander("➕ Yeni Ürün Ekle", expanded=False):
            if not profile_data.get("store_name") or not profile_data.get("chat_id"):
                st.warning("⚠️ Lütfen 'Mağaza ve Profil' sekmesinden ayarlarınızı tamamlayın.")
            else:
                with st.form("add_product_form", clear_on_submit=True):
                    new_url = st.text_input("Trendyol Ürün Linki", placeholder="https://www.trendyol.com/...")
                    
                    # 0.00 silme derdi bitti. Değer boş gelir, kullanıcı direkt yazar.
                    new_min_price = st.number_input(
                        "Dip Fiyat (Zarar Sınırı - TL)", 
                        min_value=0.0, 
                        step=1.0, 
                        value=None, 
                        placeholder="Örn: 850"
                    )
                    
                    add_product = st.form_submit_button("Ürünü Ekle")
                    
                    if add_product:
                        if new_url and new_min_price is not None and new_min_price > 0:
                            # Mükerrer Kayıt (Duplicate) Kontrolü
                            existing_urls = [item['url'].lower().strip() for item in products_data]
                            if new_url.lower().strip() in existing_urls:
                                msg = st.warning("⚠️ Bu ürün zaten takip listenizde ekli!")
                                time.sleep(2.5)
                                msg.empty()
                            else:
                                new_entry = {
                                    "url": new_url,
                                    "client_name": profile_data["store_name"],
                                    "min_price": float(new_min_price),
                                    "chat_id": profile_data["chat_id"]
                                }
                                products_data.append(new_entry)
                                save_json(PRODUCTS_FILE, products_data)
                                
                                msg = st.success("✅ Ürün eklendi! Arka planda takibe alınıyor...")
                                time.sleep(2)
                                msg.empty()
                                st.rerun()
                        else:
                            st.error("Lütfen geçerli bir link ve dip fiyat giriniz.")

        st.markdown("---")
        
        # --- ARAMA (FİLTRE) VE BAŞLIK YAN YANA ---
        col_head1, col_head2 = st.columns([1, 1])
        with col_head1:
            st.subheader(f"📋 Takipteki Ürünler ({len(products_data)} Adet)")
        with col_head2:
            search_query = st.text_input(
                "Arama", 
                placeholder="🔍 Ürün adı veya link ile ara...", 
                label_visibility="collapsed"
            )
        
        filtered_products = products_data
        if search_query:
            search_lower = search_query.lower()
            filtered_products = [
                item for item in products_data
                if search_lower in item['url'].lower() or search_lower in extract_product_name(item['url']).lower()
            ]

        # --- LİSTELEME VE DÜZENLEME ---
        if filtered_products:
            for idx, item in enumerate(filtered_products):
                display_name = extract_product_name(item['url'])
                real_idx = products_data.index(item)
                
                with st.container():
                    col_a, col_b, col_c = st.columns([5, 2, 2])
                    
                    with col_a:
                        st.markdown(f"**{display_name}**")
                        st.caption(f"[Bağlantıya Git]({item['url']})")
                    
                    with col_b:
                        st.markdown(f"📉 **Dip:** {item['min_price']} TL")
                    
                    with col_c:
                        # Düzenle ve Sil butonları için ufak bir menü (Expander)
                        with st.expander("⚙️ İşlemler", expanded=False):
                            # Düzenleme Formu
                            new_price = st.number_input(
                                "Yeni Dip Fiyat", 
                                value=None, 
                                placeholder="Örn: 850", 
                                step=1.0, 
                                key=f"edit_inp_{real_idx}"
                            )
                            if st.button("💾 Kaydet", key=f"save_btn_{real_idx}", use_container_width=True):
                                products_data[real_idx]['min_price'] = float(new_price)
                                save_json(PRODUCTS_FILE, products_data)
                                st.toast("Fiyat güncellendi!", icon="✅")
                                time.sleep(0.5)
                                st.rerun()
                                
                            st.divider() # Araya ince çizgi
                            
                            # Silme İşlemi
                            if st.button("🗑️ Ürünü Sil", key=f"delete_{real_idx}", use_container_width=True):
                                products_data.pop(real_idx)
                                save_json(PRODUCTS_FILE, products_data)
                                st.toast("Ürün silindi.", icon="🗑️")
                                time.sleep(0.5)
                                st.rerun()
                    st.divider()
        else:
            if search_query:
                st.info("Aramanızla eşleşen ürün bulunamadı.")
            else:
                st.info("Sisteme kayıtlı ürün bulunmuyor.")