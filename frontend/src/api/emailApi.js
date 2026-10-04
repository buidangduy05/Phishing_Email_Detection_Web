const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");

export async function analyzeEmail(file) {
  const formData = new FormData();
  formData.append("file", file);

  let response;
  try {
    response = await fetch(`${apiBaseUrl}/api/analyze`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error("Could not connect to the analysis service. Please try again.");
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(
      body?.message ?? body?.detail ?? `Analysis failed (${response.status}).`,
    );
  }
  if (!body || typeof body !== "object") {
    throw new Error("The analysis service returned an invalid response.");
  }

  const isPhishing = body.isPhishing ?? body.is_phishing ?? body.phishing;
  if (typeof isPhishing !== "boolean") {
    throw new Error("The analysis response did not include a phishing result.");
  }

  const featureData = body.features ?? body.indicators ?? [];
  if (!Array.isArray(featureData)) {
    throw new Error("The analysis response included invalid phishing indicators.");
  }
  const features = featureData.map((feature) => {
    if (typeof feature === "string") {
      return { title: feature, description: "" };
    }
    if (!feature || typeof feature !== "object") {
      throw new Error("The analysis response included an invalid phishing indicator.");
    }
    const title = feature.title ?? feature.name ?? "Phishing indicator";
    const description = feature.description ?? feature.detail ?? "";
    if (typeof title !== "string" || typeof description !== "string") {
      throw new Error("The analysis response included an invalid phishing indicator.");
    }
    return { title, description };
  });
  const summary = body.summary ?? body.message ?? "";
  if (typeof summary !== "string") {
    throw new Error("The analysis response included an invalid summary.");
  }

  return {
    isPhishing,
    features,
    summary,
  };
}
