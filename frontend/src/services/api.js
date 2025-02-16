// src/services/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export default api;

const API_BASE_URL = 'http://localhost:8000';

export const openDirectoryDialog = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/open-directory-dialog`);
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || error.message || 'Failed to open directory dialog';
    }
};

export const setOutputDirectory = async (path) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/set-output-directory`, { 
            path: path 
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || error.message || 'Failed to set output directory';
    }
};