import { createContext, useContext, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const name = localStorage.getItem("user_name");
    const role = localStorage.getItem("user_role");
    const token = localStorage.getItem("access_token");
    return token ? { name, role, token } : null;
  });

  const login = async (email, password) => {
    const response = await api.post("/auth/login", { email, password });
    const { access_token, name, role } = response.data;

    localStorage.setItem("access_token", access_token);
    localStorage.setItem("user_name", name);
    localStorage.setItem("user_role", role);

    setUser({ name, role, token: access_token });
    return response.data;
  };

  const signup = async (name, email, password, role) => {
    const response = await api.post("/auth/signup", {
      name,
      email,
      password,
      role,
    });
    const data = response.data;

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_name", data.name);
    localStorage.setItem("user_role", data.role);

    setUser({ name: data.name, role: data.role, token: data.access_token });
    return data;
  };

  const googleLogin = async (credential, role) => {
    const response = await api.post("/auth/google", { credential, role });
    const data = response.data;

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_name", data.name);
    localStorage.setItem("user_role", data.role);

    setUser({ name: data.name, role: data.role, token: data.access_token });
    return data;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_role");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, googleLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

