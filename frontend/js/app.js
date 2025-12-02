// ============================================
// GESTION DE L'AUTHENTIFICATION
// ============================================
const auth = {
    // Connexion avec Twitch
    async login() {
        showStatus('Redirection vers Twitch...', 'info', 'loginStatus')
        
        try {
            const { data, error } = await supabase.auth.signInWithOAuth({
                provider: 'twitch',
                options: {
                    redirectTo: window.location.origin
                }
            })

            if (error) throw error
            
            console.log('Redirection OAuth initiée')
        } catch (error) {
            console.error('Erreur de connexion:', error)
            showStatus(`❌ Erreur: ${error.message}`, 'error', 'loginStatus')
        }
    },

    // Déconnexion
    async logout() {
        showStatus('Déconnexion en cours...', 'info')
        
        try {
            const { error } = await supabase.auth.signOut()
            
            if (error) throw error
            
            showStatus('✅ Déconnexion réussie', 'success')
            showLoginSection()
        } catch (error) {
            console.error('Erreur de déconnexion:', error)
            showStatus(`❌ Erreur: ${error.message}`, 'error')
        }
    }
}


const twitchTokens = {
    // Sauvegarder les tokens Twitch dans le backend
    async saveToBackend(session) {
        if (!session?.provider_token) {
            console.warn('Pas de provider_token disponible')
            return false
        }

        try {
            showStatus('Sauvegarde des tokens Twitch...', 'info')
            
            const response = await fetch(`${CONFIG.BACKEND_URL}/auth/twitch/tokens`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`, // JWT Supabase
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    twitch_access_token: session.provider_token,
                    twitch_refresh_token: session.provider_refresh_token
                })
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || 'Erreur sauvegarde tokens')
            }

            console.log('Tokens Twitch sauvegardés')
            showStatus('Tokens Twitch sauvegardés', 'success')
            return true
            
        } catch (error) {
            console.error('Erreur sauvegarde tokens:', error)
            showStatus(`Erreur: ${error.message}`, 'error')
            return false
        }
    }
}

// ============================================
// APPELS API BACKEND
// ============================================
const api = {
    // Appeler l'endpoint /auth/me
    async callBackend() {
        showStatus('📡 Appel de l\'API backend...', 'info')
        
        try {
            const { data: { session } } = await supabase.auth.getSession()
            
            if (!session) {
                throw new Error('Pas de session active')
            }

            await twitchTokens.saveToBackend(session)

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || 'Erreur API')
            }

            showStatus('✅ Réponse reçue du backend', 'success')
            displayAPIResponse(data)
        } catch (error) {
            console.error('Erreur API:', error)
            showStatus(`❌ Erreur: ${error.message}`, 'error')
        }
    },

    // Récupérer le profil utilisateur
    async getUserProfile() {
        showStatus('👤 Récupération du profil...', 'info')
        
        try {
            const { data: { user }, error } = await supabase.auth.getUser()
            
            if (error) throw error
            
            showStatus('✅ Profil récupéré', 'success')
            displayAPIResponse({
                message: 'Profil utilisateur complet',
                user: user
            })
        } catch (error) {
            console.error('Erreur:', error)
            showStatus(`❌ Erreur: ${error.message}`, 'error')
        }
    }
}

// ============================================
// GESTION DE L'INTERFACE
// ============================================

// Afficher la section de connexion
function showLoginSection() {
    document.getElementById('loginSection').classList.remove('hidden')
    document.getElementById('dashboardSection').classList.add('hidden')
}

// Afficher la section dashboard
function showDashboardSection(user) {
    document.getElementById('loginSection').classList.add('hidden')
    document.getElementById('dashboardSection').classList.remove('hidden')
    
    // Remplir les infos utilisateur
    document.getElementById('userEmail').textContent = user.email || 'N/A'
    document.getElementById('userId').textContent = user.id || 'N/A'
    document.getElementById('userProvider').textContent = 
        user.app_metadata?.provider || 'N/A'
    document.getElementById('username').textContent = 
        user.user_metadata?.preferred_username || 
        user.user_metadata?.name || 
        'N/A'
}

// Afficher un message de statut
function showStatus(message, type = 'info', containerId = 'statusMessages') {
    const container = document.getElementById(containerId)
    const statusEl = document.createElement('div')
    statusEl.className = `status-message ${type} show`
    statusEl.textContent = message
    
    if (containerId === 'loginStatus') {
        container.innerHTML = ''
    }
    
    container.appendChild(statusEl)
    
    // Auto-suppression après 5 secondes (sauf pour loginStatus)
    if (containerId !== 'loginStatus') {
        setTimeout(() => {
            statusEl.classList.remove('show')
            setTimeout(() => statusEl.remove(), 300)
        }, 5000)
    }
}

// Afficher la réponse de l'API
function displayAPIResponse(data) {
    const responseDiv = document.getElementById('apiResponse')
    const dataDiv = document.getElementById('apiData')
    
    responseDiv.classList.remove('hidden')
    dataDiv.textContent = JSON.stringify(data, null, 2)
}

// ============================================
// ÉCOUTE DES ÉVÉNEMENTS D'AUTHENTIFICATION
// ============================================
supabase.auth.onAuthStateChange(async (event, session) => {
    console.log('Auth event:', event)
    
    if (event === 'INITIAL_SESSION' || event === 'SIGNED_IN') {
        if (session?.user) {
            console.log('✅ Utilisateur connecté:', session.user.email)
            showDashboardSection(session.user)
            
            if (event === 'SIGNED_IN') {
                await twitchTokens.saveToBackend(session)
                showStatus('✅ Connexion réussie !', 'success')
            }
        } else {
            showLoginSection()
        }
    }
    
    if (event === 'SIGNED_OUT') {
        console.log('👋 Utilisateur déconnecté')
        showLoginSection()
    }
    
    if (event === 'TOKEN_REFRESHED') {
        console.log('🔄 Token rafraîchi')
    }
})

// ============================================
// INITIALISATION AU CHARGEMENT
// ============================================
window.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Application chargée')
    
    // Vérifier la session au chargement
    const { data: { session } } = await supabase.auth.getSession()
    
    if (session?.user) {
        showDashboardSection(session.user)
    } else {
        showLoginSection()
    }
})