// ⚠️ CONFIGURATION - REMPLACE CES VALEURS
const CONFIG = {
    SUPABASE_URL: 'https://axbfethbutbrorjzwbgk.supabase.co',
    SUPABASE_ANON_KEY: 'sb_publishable_SeIwANjVYHYY5xUhMa_JGw_BA7rmQJ1',
    BACKEND_URL: 'http://localhost:8000'
}

// Vérification de la config
if (CONFIG.SUPABASE_URL.includes('xxxxx')) {
    console.error('⚠️ ERREUR: Configure SUPABASE_URL dans js/config.js')
}

if (CONFIG.SUPABASE_ANON_KEY.includes('...')) {
    console.error('⚠️ ERREUR: Configure SUPABASE_ANON_KEY dans js/config.js')
}

// Initialiser le client Supabase
const supabase = window.supabase.createClient(
    CONFIG.SUPABASE_URL,
    CONFIG.SUPABASE_ANON_KEY
)

console.log('✅ Supabase initialisé')