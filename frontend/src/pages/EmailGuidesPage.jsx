import Icon from "../components/Icon.jsx";
import emailGuides from "../data/emailGuides.js";

export default function EmailGuidesPage() {
  return (
    <main className="page-main">
      <section className="page-intro">
        <div className="eyebrow">
          <span className="eyebrow-dot" />
          GETTING STARTED
        </div>
        <h1>
          Save an email as an <span>.eml file.</span>
        </h1>
        <p>
          An EML file keeps the original message details that help our analysis.
          Choose your email app below to see how to export one.
        </p>
      </section>
      <section className="guide-layout" aria-label="Email export instructions">
        <div className="guide-list">
          {emailGuides.map((guide, index) => (
            <article className="guide-card" key={guide.id}>
              <div className={`provider-icon provider-${guide.id}`}>
                {guide.icon}
              </div>
              <div className="guide-content">
                <div className="guide-heading">
                  <div>
                    <span className="provider-label">{guide.label}</span>
                    <h2>{guide.name}</h2>
                  </div>
                  <span className="guide-index">0{index + 1}</span>
                </div>
                <ol>
                  {guide.steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
                {guide.id === "yahoo" && (
                  <p className="guide-tip">
                    Tip: menu wording can vary by Yahoo Mail version. Save the
                    complete raw message, including its headers.
                  </p>
                )}
              </div>
            </article>
          ))}
        </div>
        <aside className="guide-aside">
          <span className="aside-icon">
            <Icon name="shield" size={22} />
          </span>
          <h2>Keep the original intact</h2>
          <p>
            Upload the exported message file, not a screenshot or a copied
            snippet. The original headers can contain useful clues.
          </p>
          <div className="aside-divider" />
          <span className="aside-label">READY TO CHECK?</span>
          <a className="button button-primary button-full" href="#/analyze">
            Upload an email <Icon name="arrow" size={17} />
          </a>
          <span className="file-note">EML files only · Max 20 MB</span>
        </aside>
      </section>
    </main>
  );
}
