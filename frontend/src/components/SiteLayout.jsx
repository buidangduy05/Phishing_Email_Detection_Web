import Icon from "./Icon.jsx";

function Brand() {
  return (
    <a className="brand" href="#/" aria-label="Mailguard home">
      <span className="brand-mark">
        <Icon name="shield" size={20} />
      </span>
      <span>mailguard</span>
    </a>
  );
}

export function SiteHeader({ page }) {
  return (
    <header className="site-header">
      <div className="header-inner">
        <Brand />
        <nav className="main-nav" aria-label="Main navigation">
          <a className={page === "home" ? "active" : ""} href="#/">
            Home
          </a>
          <a className={page === "guides" ? "active" : ""} href="#/guides">
            Export an email
          </a>
          <a className={page === "analyze" ? "active" : ""} href="#/analyze">
            Analyze email
          </a>
        </nav>
        <a className="header-cta" href="#/analyze">
          <span>Check an email</span>
          <Icon name="arrow" size={16} />
        </a>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <Brand />
        <p>Safer inboxes start with a second look.</p>
        <span className="footer-note">AI-assisted email security</span>
      </div>
    </footer>
  );
}
