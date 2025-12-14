// JerryTech E-commerce JavaScript
// Gestion principale du site e-commerce

class JerryTech {
    constructor() {
        // Utiliser l'API locale en développement, ou l'URL de production
        this.apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:5000'
            : 'https://jeytech.onrender.com';
        this.cart = this.loadCart();
        this.token = localStorage.getItem('authToken');
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateCartUI();
        this.checkAuthStatus();
    }

    // ===== AUTHENTIFICATION =====
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.token;
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                this.checkAuthStatus(); // Mettre à jour l'UI immédiatement
                this.showNotification('Connexion réussie!', 'success');
                return true;
            } else {
                this.showNotification('Email ou mot de passe incorrect', 'error');
                return false;
            }
        } catch (error) {
            console.error('Erreur de connexion:', error);
            this.showNotification('Erreur de connexion', 'error');
            return false;
        }
    }

    async register(userData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const data = await response.json();
                // Stocker le token et les infos utilisateur (comme login)
                this.token = data.token;
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                this.checkAuthStatus(); // Mettre à jour l'UI immédiatement
                this.showNotification('Compte créé avec succès!', 'success');
                return data; // Retourner les données pour pouvoir les utiliser
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showNotification(errorData.error || 'Erreur lors de la création du compte', 'error');
                return false;
            }
        } catch (error) {
            console.error('Erreur d\'inscription:', error);
            this.showNotification('Erreur de création de compte', 'error');
            return false;
        }
    }


    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        this.token = null;
        this.showNotification('Déconnexion réussie', 'success');
        // Détecter si on est dans un sous-dossier et ajuster le chemin
        const isInSubfolder = window.location.pathname.includes('/pages/');
        const indexPath = isInSubfolder ? '../index.html' : 'index.html';
        setTimeout(() => window.location.href = indexPath, 1000);
    }

    checkAuthStatus() {
        const userStr = localStorage.getItem('user');

        if (userStr && this.token) {
            const userData = JSON.parse(userStr);
            this.updateAuthUI(userData);

            // Vérifier si l'utilisateur est admin
            if (userData.is_admin) {
                this.showAdminLink();
            }
        }
    }

    showAdminLink() {
        // Déterminer le chemin correct vers admin.html
        const isInSubfolder = window.location.pathname.includes('/pages/');
        const adminPath = isInSubfolder ? 'admin.html' : 'pages/admin.html';

        // Add admin link to navigation if not already present
        const navs = document.querySelectorAll('nav');
        navs.forEach(nav => {
            // Éviter les doublons
            if (!nav.querySelector('.admin-link')) {
                const adminLink = document.createElement('a');
                adminLink.href = adminPath;
                adminLink.innerHTML = '<i data-feather="shield" class="h-4 w-4 inline mr-1"></i> Admin';

                // Style différent pour desktop vs mobile si nécessaire, mais ici on garde simple
                adminLink.className = 'admin-link text-red-600 font-semibold hover:text-red-700 transition-colors flex items-center bg-red-50 px-3 py-1 rounded-full cursor-pointer';

                // Ajouter au début ou à la fin de la nav
                nav.appendChild(adminLink);

                // Rafraichir les icônes feather si chargé
                if (window.feather) feather.replace();
            }
        });
    }

    updateAuthUI(userData) {
        const authButtons = document.querySelectorAll('.auth-buttons');
        authButtons.forEach(button => {
            if (button.querySelector('.login-btn')) {
                // Determine path to account page based on current location
                const isInSubfolder = window.location.pathname.includes('/pages/');
                const accountPath = isInSubfolder ? 'account.html' : 'pages/account.html';

                button.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <a href="${accountPath}" class="text-sm font-medium text-gray-700 hover:text-blue-600 flex items-center transition-colors">
                            <i data-feather="user" class="h-4 w-4 mr-1"></i>
                            ${userData.name}
                        </a>
                        <button onclick="jerryTech.logout()" class="text-red-500 hover:text-red-700 text-sm font-medium transition-colors">Déconnexion</button>
                    </div>
                `;
                // Refresh icons
                if (window.feather) feather.replace();
            }
        });
    }

    // ===== GESTION DU PANIER =====
    loadCart() {
        const savedCart = localStorage.getItem('jerrytech-cart');
        return savedCart ? JSON.parse(savedCart) : [];
    }

    saveCart() {
        localStorage.setItem('jerrytech-cart', JSON.stringify(this.cart));
        this.updateCartUI();
    }

    addToCart(product, quantity = 1) {
        const existingItem = this.cart.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.cart.push({
                ...product,
                quantity: quantity
            });
        }

        this.saveCart();
        this.showNotification('Produit ajouté au panier!', 'success');
        this.animateCartIcon();
    }

    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.showNotification('Produit retiré du panier', 'info');
    }

    updateQuantity(productId, quantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = quantity;
                this.saveCart();
            }
        }
    }

    getCartTotal() {
        return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    getCartCount() {
        return this.cart.reduce((count, item) => count + item.quantity, 0);
    }

    updateCartUI() {
        const cartCountElements = document.querySelectorAll('.cart-count');
        const cartTotalElements = document.querySelectorAll('.cart-total');
        const cartCount = this.getCartCount();

        cartCountElements.forEach(element => {
            element.textContent = cartCount;
            element.style.display = cartCount > 0 ? 'block' : 'none';
        });

        cartTotalElements.forEach(element => {
            element.textContent = this.formatPrice(this.getCartTotal());
        });
    }

    animateCartIcon() {
        const cartIcon = document.querySelector('.cart-icon');
        if (cartIcon) {
            cartIcon.classList.add('animate-bounce');
            setTimeout(() => cartIcon.classList.remove('animate-bounce'), 1000);
        }
    }

    // ===== PRODUITS ET API =====
    async getProducts(params = {}) {
        try {
            // Convertir les paramètres pour l'API
            const apiParams = {};
            if (params.category) apiParams.category = params.category;
            if (params.search) apiParams.search = params.search;
            if (params.limit) apiParams.limit = params.limit;
            if (params.featured) apiParams.featured = params.featured;

            const queryString = new URLSearchParams(apiParams).toString();
            const response = await fetch(`${this.apiBaseUrl}/api/products?${queryString}`);

            if (response.ok) {
                const products = await response.json();
                // Adapter les données de l'API au format attendu par le frontend
                return products.map(p => ({
                    id: p.id,
                    name: p.name,
                    description: p.description || '',
                    price: p.price,
                    originalPrice: p.original_price,
                    category: p.category,
                    brand: p.brand,
                    image: p.image || 'https://via.placeholder.com/300x300/1a73e8/ffffff?text=Produit',
                    images: p.images, // Add this line
                    inStock: p.in_stock,
                    stock: p.stock,
                    rating: p.rating || 0,
                    featured: p.featured || false,
                    createdAt: p.created_at
                }));
            } else {
                console.error('Erreur lors de la récupération des produits');
                return this.getMockProducts(); // Fallback pour démo
            }
        } catch (error) {
            console.error('Erreur API produits:', error);
            return this.getMockProducts(); // Fallback pour démo
        }
    }

    async getProduct(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/products/${id}`);

            if (response.ok) {
                const product = await response.json();
                // Adapter les données de l'API au format attendu par le frontend
                return {
                    id: product.id,
                    name: product.name,
                    description: product.description || '',
                    price: product.price,
                    originalPrice: product.original_price,
                    category: product.category,
                    brand: product.brand,
                    image: product.image || 'https://via.placeholder.com/300x300/1a73e8/ffffff?text=Produit',
                    images: product.images, // Add this line
                    inStock: product.in_stock,
                    stock: product.stock,
                    rating: product.rating || 0,
                    featured: product.featured || false,
                    createdAt: product.created_at
                };
            } else {
                console.error('Produit non trouvé');
                return null;
            }
        } catch (error) {
            console.error('Erreur API produit:', error);
            return this.getMockProduct(id); // Fallback pour démo
        }
    }

    // ===== COMMANDES =====
    async createOrder(orderData) {
        if (!this.token) {
            this.showNotification('Veuillez vous connecter pour passer commande', 'error');
            return false;
        }

        try {
            // Adapter les données du panier au format API
            const apiOrderData = {
                items: this.cart.map(item => ({
                    product_id: item.id,
                    quantity: item.quantity
                })),
                shipping_address: orderData.shipping_address || '',
                phone: orderData.phone || ''
            };

            const response = await fetch(`${this.apiBaseUrl}/api/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(apiOrderData)
            });

            if (response.ok) {
                const data = await response.json();
                this.cart = [];
                this.saveCart();
                this.showNotification('Commande passée avec succès!', 'success');
                return data;
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showNotification(errorData.detail || 'Erreur lors de la commande', 'error');
                return false;
            }
        } catch (error) {
            console.error('Erreur commande:', error);
            this.showNotification('Erreur lors de la commande', 'error');
            return false;
        }
    }

    // ===== CONTACT =====
    async sendContact(formData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showNotification('Message envoyé avec succès!', 'success');
                return true;
            } else {
                this.showNotification('Erreur lors de l\'envoi du message', 'error');
                return false;
            }
        } catch (error) {
            console.error('Erreur contact:', error);
            this.showNotification('Erreur lors de l\'envoi', 'error');
            return false;
        }
    }

    // ===== UTILITAIRES =====
    formatPrice(price) {
        return new Intl.NumberFormat('fr-HT', {
            style: 'currency',
            currency: 'HTG',
            minimumFractionDigits: 0
        }).format(price);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 ${type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
                'bg-blue-500 text-white'
            }`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    setupEventListeners() {
        // Recherche
        const searchForms = document.querySelectorAll('.search-form');
        searchForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const query = form.querySelector('input').value;
                window.location.href = `products.html?search=${encodeURIComponent(query)}`;
            });
        });
    }

    // Données mock pour démonstration
    getMockProducts() {
        return [
            {
                id: 1,
                name: "iPhone 15 Pro",
                price: 85000,
                originalPrice: 95000,
                image: "https://via.placeholder.com/300x300/1a73e8/ffffff?text=iPhone+15+Pro",
                category: "Smartphones",
                rating: 4.8,
                inStock: true,
                description: "Le dernier iPhone avec puce A17 Pro"
            },
            {
                id: 2,
                name: "MacBook Air M2",
                price: 120000,
                originalPrice: 135000,
                image: "https://via.placeholder.com/300x300/1a73e8/ffffff?text=MacBook+Air+M2",
                category: "Ordinateurs",
                rating: 4.9,
                inStock: true,
                description: "Laptop ultra-fin avec puce M2"
            },
            {
                id: 3,
                name: "AirPods Pro",
                price: 25000,
                originalPrice: 28000,
                image: "https://via.placeholder.com/300x300/1a73e8/ffffff?text=AirPods+Pro",
                category: "Audio",
                rating: 4.7,
                inStock: true,
                description: "Écouteurs avec réduction de bruit active"
            }
        ];
    }

    getMockProduct(id) {
        const products = this.getMockProducts();
        return products.find(p => p.id == id) || null;
    }
}

// Initialisation globale
let jerryTech;

document.addEventListener('DOMContentLoaded', () => {
    jerryTech = new JerryTech();
});

// Fonctions utilitaires globales
function addToCart(productId) {
    const product = jerryTech.getMockProduct(productId);
    if (product) {
        jerryTech.addToCart(product);
    }
}

function removeFromCart(productId) {
    jerryTech.removeFromCart(productId);
}

function updateQuantity(productId, quantity) {
    jerryTech.updateQuantity(productId, parseInt(quantity));
}