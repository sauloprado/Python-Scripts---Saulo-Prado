import { useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  Download,
  FileText,
  LogOut,
  Newspaper,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react";
import {
  generateNews,
  getLatestNews,
  getRuns,
  getSession,
  login,
  logout,
} from "./api";

const defaultTopics = "ChatGPT, Claude AI, OpenAI, Anthropic, inteligencia artificial";

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function filenameFromPath(path) {
  return (path || "").split(/[\\/]/).pop();
}

function topicInitial(topic) {
  return (topic || "IA").slice(0, 2).toUpperCase();
}

function LoginView({ onLogin }) {
  const [username, setUsername] = useState("saulo");
  const [password, setPassword] = useState("trocar123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await login(username, password);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel">
        <div className="brand-mark">
          <Newspaper size={24} />
        </div>
        <h1>Noticias IA Web</h1>
        <form onSubmit={handleSubmit} className="login-form">
          <label>
            Usuario
            <input value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
          <label>
            Senha
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button type="submit" className="primary-button" disabled={loading}>
            <ShieldCheck size={18} />
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  );
}

function ControlPanel({ onGenerate, loading }) {
  const [maxArticles, setMaxArticles] = useState(12);
  const [daysBack, setDaysBack] = useState(1);
  const [topics, setTopics] = useState(defaultTopics);

  function handleSubmit(event) {
    event.preventDefault();
    onGenerate({
      max_articles: maxArticles,
      days_back: daysBack,
      topics,
    });
  }

  return (
    <form className="control-panel" onSubmit={handleSubmit}>
      <label className="control-wide">
        Topicos
        <div className="input-icon">
          <Search size={17} />
          <input value={topics} onChange={(event) => setTopics(event.target.value)} />
        </div>
      </label>
      <label>
        Noticias
        <input
          type="number"
          min="1"
          max="30"
          value={maxArticles}
          onChange={(event) => setMaxArticles(Number(event.target.value))}
        />
      </label>
      <label>
        Dias
        <input
          type="number"
          min="1"
          max="7"
          value={daysBack}
          onChange={(event) => setDaysBack(Number(event.target.value))}
        />
      </label>
      <button type="submit" className="primary-button" disabled={loading}>
        <RefreshCw size={18} className={loading ? "spin" : ""} />
        {loading ? "Buscando..." : "Gerar noticias"}
      </button>
    </form>
  );
}

function NewsCard({ article }) {
  return (
    <article className="news-card">
      <div className="media-frame">
        {article.image_url ? (
          <img src={article.image_url} alt="" loading="lazy" />
        ) : (
          <div className="topic-visual">
            <span>{topicInitial(article.topic)}</span>
          </div>
        )}
      </div>
      <div className="news-content">
        <div className="meta-row">
          <span>{article.source}</span>
          <span>{formatDate(article.published_at)}</span>
        </div>
        <h2>{article.title}</h2>
        <p>{article.summary}</p>
        <div className="card-actions">
          <span className="topic-pill">{article.topic}</span>
          <a href={article.url} target="_blank" rel="noreferrer">
            Abrir
            <ArrowUpRight size={16} />
          </a>
        </div>
      </div>
    </article>
  );
}

function RunsPanel({ runs }) {
  return (
    <aside className="runs-panel">
      <div className="section-title">
        <FileText size={18} />
        <h2>Arquivos</h2>
      </div>
      <div className="runs-list">
        {runs.map((run) => {
          const filename = filenameFromPath(run.file_path);
          return (
            <a key={run.id} href={`/api/files/${encodeURIComponent(filename)}`} className="run-item">
              <div>
                <strong>{formatDate(run.generated_at)}</strong>
                <span>{run.total_articles} noticias</span>
              </div>
              <Download size={17} />
            </a>
          );
        })}
      </div>
    </aside>
  );
}

function Dashboard({ user, onLogout }) {
  const [articles, setArticles] = useState([]);
  const [run, setRun] = useState(null);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const stats = useMemo(
    () => [
      { label: "Ultima busca", value: run ? formatDate(run.generated_at) : "-" },
      { label: "Noticias", value: articles.length },
      { label: "Arquivo", value: run ? filenameFromPath(run.file_path) : "-" },
    ],
    [articles.length, run],
  );

  async function loadData() {
    const [newsData, runsData] = await Promise.all([getLatestNews(), getRuns()]);
    setArticles(newsData.articles || []);
    setRun(newsData.run);
    setRuns(runsData.runs || []);
  }

  async function handleGenerate(payload) {
    setLoading(true);
    setMessage("");

    try {
      const data = await generateNews(payload);
      setArticles(data.articles || []);
      setRun(data.run);
      const runsData = await getRuns();
      setRuns(runsData.runs || []);
      setMessage("Noticias atualizadas e arquivo TXT salvo.");
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    await logout();
    onLogout();
  }

  useEffect(() => {
    loadData().catch(() => {});
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-inline">
          <span className="brand-icon">
            <Newspaper size={21} />
          </span>
          <div>
            <strong>Noticias IA Web</strong>
            <span>{user.username}</span>
          </div>
        </div>
        <button type="button" className="icon-button" onClick={handleLogout} title="Sair">
          <LogOut size={19} />
        </button>
      </header>

      <section className="workspace">
        <div className="main-column">
          <section className="hero-band">
            <div>
              <p>Leitura local</p>
              <h1>Noticias de IA organizadas para ler sem ruido.</h1>
            </div>
            <div className="stats-grid">
              {stats.map((item) => (
                <div className="stat" key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </section>

          <ControlPanel onGenerate={handleGenerate} loading={loading} />
          {message && <p className="status-message">{message}</p>}

          <section className="news-grid">
            {articles.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
            {!articles.length && (
              <div className="empty-state">
                <Newspaper size={28} />
                <span>Nenhuma noticia carregada.</span>
              </div>
            )}
          </section>
        </div>

        <RunsPanel runs={runs} />
      </section>
    </main>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    getSession()
      .then((data) => setUser(data.user))
      .finally(() => setChecking(false));
  }, []);

  if (checking) {
    return (
      <main className="loading-screen">
        <RefreshCw className="spin" size={28} />
      </main>
    );
  }

  if (!user) {
    return <LoginView onLogin={setUser} />;
  }

  return <Dashboard user={user} onLogout={() => setUser(null)} />;
}
