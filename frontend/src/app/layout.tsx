import type { Metadata } from "next";
import { Inter, Noto_Serif_SC, JetBrains_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { TopNav } from "@/components/top-nav";
import { Sidebar } from "@/components/sidebar";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const notoSerifSC = Noto_Serif_SC({
  variable: "--font-noto-serif-sc",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FengxianCyberTaoist - AI 命理预测平台",
  description: "结合紫微斗数与多智能体社会模拟的 AI 预测平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${notoSerifSC.variable} ${jetbrainsMono.variable} min-h-full antialiased`}
      >
        <QueryProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
          >
            <div className="flex min-h-screen flex-col">
              <TopNav />
              <div className="flex flex-1">
                <Sidebar />
                <main className="flex-1 overflow-auto bg-background">
                  <div className="container mx-auto p-4 md:p-6 lg:p-8">
                    {children}
                  </div>
                </main>
              </div>
            </div>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
