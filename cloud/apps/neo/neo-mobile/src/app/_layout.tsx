import "../global.css";
import React from "react";
import * as Linking from "expo-linking";
import { Slot } from "expo-router";
import { AuthProvider } from "@/context/auth/context";
import { GluestackUIProvider } from "@/components/ui/gluestack-ui-provider";
import { SafeAreaView, StatusBar } from "react-native";

type Theme = "dark" | "light";
type ThemeContextType = {
  colorMode?: Theme;
  toggleColorMode?: () => void;
};

let defaultTheme: Theme = "dark";

Linking.getInitialURL().then((url: any) => {
  let { queryParams } = Linking.parse(url) as any;
  defaultTheme = queryParams?.iframeMode ?? defaultTheme;
});

export const ThemeContext = React.createContext<ThemeContextType>({
  colorMode: defaultTheme,
  toggleColorMode: () => { },
});

export default function App() {
  const [colorMode, setColorMode] = React.useState<Theme>(
    defaultTheme
  );

  const toggleColorMode = async () => {
    setColorMode((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ colorMode, toggleColorMode }}>
      <GluestackUIProvider mode={colorMode}>
        <AuthProvider>
          <SafeAreaView
            className={`${colorMode === "light" ? "bg-white" : "bg-[#171717]"
              } flex-1 overflow-hidden`}>
            <StatusBar />
            <Slot />
          </SafeAreaView>
        </AuthProvider>
      </GluestackUIProvider>
    </ThemeContext.Provider>
  );
}