export const handleFetch = async ({ url, method = "POST", body, token }) => {
  const response = await fetch(url, {
    method,
    body,
    headers: {
      Authorization: "Bearer " + token,
    },
  });

  if (!response.ok) {
    throw new Error(response.status + ": " + response.statusText);
  }

  return response.json();
};
