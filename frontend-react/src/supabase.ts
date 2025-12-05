// supabase.ts
import { createClient } from '@supabase/supabase-js'

// 🔍 DEBUG : Affiche les variables
console.log('🔍 VITE_SUPABASE_URL:', import.meta.env.VITE_SUPABASE_URL)
console.log('🔍 VITE_SUPABASE_API_KEY:', import.meta.env.VITE_SUPABASE_API_KEY)
console.log('🔍 Toutes les env:', import.meta.env)

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_PUB_API_KEY

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Variables manquantes!')
  console.error('URL:', supabaseUrl)
  console.error('KEY:', supabaseKey)
  throw new Error('Missing Supabase credentials')
}

export const supabase = createClient(supabaseUrl, supabaseKey)
