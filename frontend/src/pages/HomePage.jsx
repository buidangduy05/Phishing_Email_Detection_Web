import Icon from "../components/Icon.jsx";

export default function HomePage() {
  return (
    <>
      <main>
        <section className="hero">
          <div className="hero-grid">
            <div className="hero-copy">
              <div className="eyebrow">
                <span className="eyebrow-dot" />
                AI-POWERED EMAIL PROTECTION
              </div>
              <h1>
                A safer inbox
                <br />
                starts <span>with a check.</span>
              </h1>
              <p className="hero-description">
                Spot suspicious emails before they catch you off guard. Upload
                an email file and let AI uncover the warning signs.
              </p>
              <div className="hero-actions">
                <a className="button button-primary" href="#/analyze">
                  Analyze an email <Icon name="arrow" size={18} />
                </a>
                <a className="button button-secondary" href="#/guides">
                  How to get an email file
                </a>
              </div>
              <div className="hero-assurance">
                <span className="assurance-icon">
                  <Icon name="shield" size={16} />
                </span>
                <span>Check the signals. Make your own call.</span>
              </div>
            </div>
            <div className="hero-art" aria-label="Email security illustration">
              <div className="art-orbit orbit-one" />
              <div className="art-orbit orbit-two" />
              <div className="art-glow" />
              <div className="mail-card">
                <div className="mail-card-top">
                  <span className="mail-icon">
                    <Icon name="mail" size={23} />
                  </span>
                  <span className="mail-dots">•••</span>
                </div>
                <div className="mail-line mail-line-long" />
                <div className="mail-line mail-line-short" />
                <div className="mail-body">
                  <div className="mail-line" />
                  <div className="mail-line mail-line-mid" />
                  <div className="mail-line mail-line-long" />
                </div>
                <div className="mail-button">View secure document</div>
                <div className="mail-warning">
                  <span className="warning-symbol">!</span>
                  <span>Unusual sender detected</span>
                </div>
              </div>
              <div className="shield-bubble">
                <Icon name="shield" size={34} />
                <span className="bubble-check">
                  <Icon name="check" size={15} />
                </span>
              </div>
              <div className="sparkle sparkle-one">✳</div>
              <div className="sparkle sparkle-two">✦</div>
              <div className="art-caption">
                <span className="caption-pulse" />
                Look closer. Stay safer.
              </div>
            </div>
          </div>
        </section>

        <section className="how-section">
          <div className="section-heading">
            <span className="section-kicker">SIMPLE BY DESIGN</span>
            <h2>Three steps to a clearer picture</h2>
            <p>No security expertise needed. Just the email you want to check.</p>
          </div>
          <div className="steps-grid">
            <article className="step-card">
              <span className="step-number">01</span>
              <div className="step-icon">
                <Icon name="mail" size={22} />
              </div>
              <h3>Save your email</h3>
              <p>Export a message from your mail app as an .eml file.</p>
            </article>
            <article className="step-card">
              <span className="step-number">02</span>
              <div className="step-icon">
                <Icon name="upload" size={22} />
              </div>
              <h3>Upload it here</h3>
              <p>We check the file and analyze its contents for warning signs.</p>
            </article>
            <article className="step-card">
              <span className="step-number">03</span>
              <div className="step-icon">
                <Icon name="shield" size={22} />
              </div>
              <h3>Review the signals</h3>
              <p>See the result and the indicators behind the assessment.</p>
            </article>
          </div>
        </section>

        <section className="home-cta">
          <div className="cta-shield">
            <Icon name="shield" size={26} />
          </div>
          <div>
            <span className="section-kicker">WHEN SOMETHING FEELS OFF</span>
            <h2>Trust your instincts. Check the email.</h2>
            <p>Start with an .eml file from Gmail, Yahoo, Thunderbird, or Outlook.</p>
          </div>
          <a className="button button-primary" href="#/analyze">
            Get started <Icon name="arrow" size={18} />
          </a>
        </section>
      </main>
    </>
  );
}
