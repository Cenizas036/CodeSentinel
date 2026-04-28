const DRIVE_API_URL = 'https://www.googleapis.com/drive/v3';
const UPLOAD_API_URL = 'https://www.googleapis.com/upload/drive/v3';

// Helper to get headers
const getHeaders = () => {
  const token = localStorage.getItem('googleOAuthToken');
  if (!token) throw new Error('Not authenticated with Google Drive');
  
  return {
    'Authorization': `Bearer ${token}`
  };
};

/**
 * Lists files from Google Drive
 * Only fetches files that the app has created (due to drive.file scope)
 */
export const listFiles = async () => {
  try {
    const response = await fetch(`${DRIVE_API_URL}/files?q=mimeType!='application/vnd.google-apps.folder'&fields=files(id, name, mimeType, modifiedTime)&orderBy=modifiedTime desc`, {
      headers: getHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to fetch files');
    const data = await response.json();
    return data.files || [];
  } catch (error) {
    console.error('Error fetching files:', error);
    throw error;
  }
};

/**
 * Reads the content of a specific file
 */
export const readFile = async (fileId) => {
  try {
    const response = await fetch(`${DRIVE_API_URL}/files/${fileId}?alt=media`, {
      headers: getHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to read file');
    const content = await response.text();
    return content;
  } catch (error) {
    console.error('Error reading file:', error);
    throw error;
  }
};

/**
 * Creates a new file in Google Drive
 */
export const createFile = async (name, content, mimeType = 'text/plain') => {
  try {
    // 1. Create file metadata
    const metadata = { name, mimeType };
    
    // We use a multipart upload to send metadata + content
    const boundary = '-------314159265358979323846';
    const delimiter = `\r\n--${boundary}\r\n`;
    const closeDelimiter = `\r\n--${boundary}--`;

    const multipartRequestBody =
      delimiter +
      'Content-Type: application/json\r\n\r\n' +
      JSON.stringify(metadata) +
      delimiter +
      `Content-Type: ${mimeType}\r\n\r\n` +
      content +
      closeDelimiter;

    const response = await fetch(`${UPLOAD_API_URL}/files?uploadType=multipart`, {
      method: 'POST',
      headers: {
        ...getHeaders(),
        'Content-Type': `multipart/related; boundary=${boundary}`
      },
      body: multipartRequestBody
    });

    if (!response.ok) throw new Error('Failed to create file');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error creating file:', error);
    throw error;
  }
};

/**
 * Updates an existing file in Google Drive
 */
export const saveFile = async (fileId, content, mimeType = 'text/plain') => {
  try {
    const response = await fetch(`${UPLOAD_API_URL}/files/${fileId}?uploadType=media`, {
      method: 'PATCH',
      headers: {
        ...getHeaders(),
        'Content-Type': mimeType
      },
      body: content
    });

    if (!response.ok) throw new Error('Failed to save file');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving file:', error);
    throw error;
  }
};
