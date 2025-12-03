import { useEffect, useState } from 'react'
import { supabase } from './supabase'
import type { User, Session } from '@supabase/supabase-js'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  // 🔥 Fonction pour sauvegarder les tokens au backend
  const saveTwitchTokens = async (session: Session) => {
    if (!session.provider_token) {
      console.warn('⚠️ Pas de provider_token disponible')
      return
    }

    try {
      console.log('🔑 Envoi des tokens au backend...')
      
      const response = await fetch('http://localhost:8000/auth/me', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          twitch_access_token: session.provider_token,
          twitch_refresh_token: session.provider_refresh_token
        })

       
      })

      const data = await response.json()
      console.log('✅ Réponse backend:', data)
      alert('✅ Tokens Twitch sauvegardés !')
      
    } catch (error) {
      console.error('❌ Erreur:', error)
      alert('❌ Erreur envoi tokens')
    }
  }

  // 🔥 Écouter les changements d'auth
  useEffect(() => {
    // Session initiale
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Écouter les events
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('🔔 Auth event:', event)
        
        setSession(session)
        setUser(session?.user ?? null)
        
        // 🎯 CRUCIAL : Sauvegarder au premier login
        if (event === 'SIGNED_IN' && session) {
          console.log('🔍 Provider token:', session.provider_token)
          await saveTwitchTokens(session)
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  // 🔥 Login Twitch
  const login = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'twitch',
      options: {
        redirectTo: window.location.origin,
        scopes: 'channel:manage:clips editor:manage:clips'
      }
    })

    
    
  }

  // 🔥 Logout
  const logout = async () => {
    await supabase.auth.signOut()
  }

  if (loading) return <div>Chargement...</div>

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>Test Auth Twitch</h1>

      {!user ? (
        <div>
          <p>Pas connecté</p>
          <button onClick={login} style={{ padding: '10px 20px', fontSize: '16px' }}>
            Se connecter avec Twitch
          </button>
        </div>
      ) : (
        <div>
          <h2> Connecté !</h2>
          <p><strong>Username:</strong> {user.user_metadata?.preferred_username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>User ID:</strong> {user.id}</p>
          
          <hr />
          
          <h3>Debug Session</h3>
          <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
            {JSON.stringify({
              has_provider_token: !!session?.provider_token,
              provider_token_preview: session?.provider_token?.substring(0, 20) + '...',
              provider: user.app_metadata?.provider
            }, null, 2)}
          </pre>

          <button onClick={logout} style={{ padding: '10px 20px', fontSize: '16px' }}>
            Déconnexion
          </button>
        </div>
      )}
    </div>
  )
}

export default App
