// State Variables
let currentCategory = "";
let currentCursor = null;
let currentLimit = 50;
let displayedProductsCount = 0;
let isFetching = false;

// DOM Elements
const productsGrid = document.getElementById("products-grid");
const loader = document.getElementById("loader");
const loadMoreBtn = document.getElementById("load-more-btn");
const displayedCountEl = document.getElementById("displayed-count");
const categoryPills = document.querySelectorAll(".filter-pill");
const limitSelect = document.getElementById("limit-select");
const injectBtn = document.getElementById("inject-btn");
const simulationToast = document.getElementById("simulation-toast");

// Fetch Products from API
async function fetchProducts(append = false) {
    if (isFetching) return;
    
    isFetching = true;
    loader.classList.remove("hidden");
    loadMoreBtn.disabled = true;
    
    if (!append) {
        productsGrid.innerHTML = "";
        displayedProductsCount = 0;
        currentCursor = null;
    }
    
    try {
        // Build query string
        let url = `/api/products?limit=${currentLimit}`;
        if (currentCategory) {
            url += `&category=${encodeURIComponent(currentCategory)}`;
        }
        if (currentCursor) {
            url += `&cursor=${encodeURIComponent(currentCursor)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Render cards
        renderProducts(data.products, append);
        
        // Update state
        currentCursor = data.next_cursor;
        displayedProductsCount += data.products.length;
        displayedCountEl.textContent = displayedProductsCount;
        
        // Show or hide "Load More" button
        if (currentCursor) {
            loadMoreBtn.style.display = "flex";
        } else {
            loadMoreBtn.style.display = "none";
        }
        
    } catch (error) {
        console.error("Error loading products:", error);
        if (!append) {
            productsGrid.innerHTML = `
                <div class="error-state">
                    <p>Failed to load products. Make sure the backend server is running.</p>
                </div>
            `;
        }
    } finally {
        isFetching = false;
        loader.classList.add("hidden");
        loadMoreBtn.disabled = false;
    }
}

// Render Product Cards
function renderProducts(products, append) {
    if (products.length === 0 && !append) {
        productsGrid.innerHTML = `
            <div class="empty-state">
                <p>No products found in this category.</p>
            </div>
        `;
        return;
    }
    
    const fragment = document.createDocumentFragment();
    
    products.forEach(product => {
        const card = document.createElement("div");
        card.className = "product-card";
        
        // Determine if it was simulated/injected in real-time
        const isInjected = product.name.includes("New-Release") || 
                           product.name.includes("Hot-Item") || 
                           product.name.includes("Concurrently-Added") || 
                           product.name.includes("Real-Time") || 
                           product.name.includes("Fresh-Stock");
                           
        // Parse time nicely
        const dateObj = new Date(product.created_at);
        const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const dateStr = dateObj.toLocaleDateString([], { month: 'short', day: 'numeric' });
        
        let badgeHtml = "";
        if (isInjected) {
            badgeHtml = `<span class="badge-new">New</span>`;
            card.classList.add("simulated-card");
        }
        
        card.innerHTML = `
            ${badgeHtml}
            <div class="card-header">
                <span class="card-category">${escapeHtml(product.category)}</span>
                <span class="card-price">$${product.price.toFixed(2)}</span>
            </div>
            <h3 class="card-title">${escapeHtml(product.name)}</h3>
            <div class="card-footer">
                <div class="card-time">
                    <span>📅</span>
                    <span>${dateStr} at ${timeStr}</span>
                </div>
                <span class="card-id">ID: ${product.id.substring(0, 8)}...</span>
            </div>
        `;
        
        fragment.appendChild(card);
    });
    
    productsGrid.appendChild(fragment);
}

// Helper to escape HTML characters (prevent XSS)
function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}

// Event Listeners for Filters
categoryPills.forEach(pill => {
    pill.addEventListener("click", (e) => {
        // Toggle active class
        categoryPills.forEach(p => p.classList.remove("active"));
        e.currentTarget.classList.add("active");
        
        // Update category and reload catalog
        currentCategory = e.currentTarget.getAttribute("data-category");
        fetchProducts(false);
    });
});

// Event Listener for Limit Change
limitSelect.addEventListener("change", (e) => {
    currentLimit = parseInt(e.target.value, 10);
    fetchProducts(false);
});

// Event Listener for Load More
loadMoreBtn.addEventListener("click", () => {
    fetchProducts(true);
});

// Event Listener for Inject Simulation Button
injectBtn.addEventListener("click", async () => {
    injectBtn.disabled = true;
    const btnText = injectBtn.querySelector(".btn-text");
    const originalText = btnText.textContent;
    btnText.textContent = "Injecting...";
    
    try {
        const response = await fetch("/api/products/inject", { method: "POST" });
        if (response.ok) {
            // Show toast message
            simulationToast.classList.remove("hidden");
            
            // Auto hide after 8 seconds
            setTimeout(() => {
                simulationToast.classList.add("hidden");
            }, 8000);
        } else {
            console.error("Failed to inject products");
        }
    } catch (err) {
        console.error("Error during injection simulation:", err);
    } finally {
        injectBtn.disabled = false;
        btnText.textContent = originalText;
    }
});

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
    fetchProducts(false);
});
