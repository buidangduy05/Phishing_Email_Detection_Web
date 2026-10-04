import { useEffect, useState } from "react";
import { SiteFooter, SiteHeader } from "./components/SiteLayout.jsx";
import AnalysisPage from "./pages/AnalysisPage.jsx";
import EmailGuidesPage from "./pages/EmailGuidesPage.jsx";
import HomePage from "./pages/HomePage.jsx";

function pageFromHash() {
  const page = window.location.hash.replace(/^#\/?/, "");
  return page === "guides" || page === "analyze" ? page : "home";
}

export default function App() {
  const [page, setPage] = useState(pageFromHash);

  useEffect(() => {
    const syncPage = () => setPage(pageFromHash());
    window.addEventListener("hashchange", syncPage);
    return () => window.removeEventListener("hashchange", syncPage);
  }, []);

  return (
    <div className="app-shell">
      <SiteHeader page={page} />
      {page === "guides" ? (
        <EmailGuidesPage />
      ) : page === "analyze" ? (
        <AnalysisPage />
      ) : (
        <HomePage />
      )}
      <SiteFooter />
    </div>
  );
}
