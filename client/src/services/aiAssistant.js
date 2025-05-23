import api from "./api";

// AI Assistant API service
export const aiAssistantApi = {
  // Chat with AI Assistant
  sendMessage: (sessionId, userQuery, subject, learnerType = "medium") =>
    api.post("/services/chat", null, {
      params: {
        session_id: sessionId,
        user_query: userQuery,
        subject: subject,
        learner_type: learnerType,
      },
    }),

  // Get all user sessions
  getSessions: () => api.get("/services/sessions"),
  // Create a new session
  createSession: (userId) =>
    api.post("/services/session/create", null, {
      params: {
        user_id: userId,
      },
    }),

  // Delete a session
  deleteSession: (userId, sessionId) =>
    api.delete("/services/session/delete", {
      params: {
        user_id: userId,
        session_id: sessionId,
      },
    }),

  // Get suggestions based on subject
  getRecommendations: (subject, learnerType = "medium") =>
    api.post("/services/recommendations", null, {
      params: {
        subject: subject,
        learner_type: learnerType,
      },
    }),

  // Get autocomplete suggestions for partial query
  getAutocompleteSuggestions: (userQueryPartial, subject) =>
    api.post("/services/autocomplete", null, {
      params: {
        user_query_partial: userQueryPartial,
        subject: subject,
      },
    }),

  // Upload a textbook/PDF
  uploadTextbook: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/services/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

export default aiAssistantApi;
