import { createContext, useContext } from 'react';

// A autenticação real será conectada à API em uma etapa posterior.
// Não há usuário fictício nem perfil concedido neste contexto.
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  return <AuthContext.Provider value={null}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}