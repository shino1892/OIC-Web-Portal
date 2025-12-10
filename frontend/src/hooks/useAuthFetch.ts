import { useRouter } from "next/navigation";
import { useCallback } from "react";

export const useAuthFetch = () => {
  const router = useRouter();

  const authFetch = useCallback(
    async (url: string, options: RequestInit = {}) => {
      const token = localStorage.getItem("token");

      const headers = new Headers(options.headers);
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }

      const res = await fetch(url, {
        ...options,
        headers,
      });

      if (res.status === 401) {
        localStorage.removeItem("token");
        window.dispatchEvent(new Event("auth-change"));
        router.push("/login");
      }

      return res;
    },
    [router]
  );

  return authFetch;
};
