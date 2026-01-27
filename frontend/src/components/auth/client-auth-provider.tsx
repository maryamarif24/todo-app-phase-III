'use client';

import { AuthProvider } from './auth-provider';
import { ReactNode, useEffect, useState } from 'react';

export function ClientAuthProvider({ children }: { children: ReactNode }) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    // Render nothing on the server and during initial client render
    return null;
  }

  return <AuthProvider>{children}</AuthProvider>;
}