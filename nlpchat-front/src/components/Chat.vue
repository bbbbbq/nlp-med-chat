<template>
  <div 
    class="chat-container"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <div v-if="isDragging" class="drag-overlay">
      <p>将文件拖放到此处以上传</p>
    </div>
    <div class="chat-header">
      <h2>智能对话</h2>
      <p>与 AI 助手进行实时交流</p>
    </div>
    <div class="messages-area" ref="messagesArea">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.sender">
        <div class="message-bubble">
          <p v-if="message.sender !== 'ai'">{{ message.text }}</p>
<div v-else v-html="renderMarkdown(message.text)"></div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <div class="textarea-wrapper">
                <div v-if="stagedFiles.length > 0" class="staged-files-grid">
          <div v-for="(url, index) in stagedFileUrls" :key="index" class="staged-file-preview">
            <img :src="url" class="file-thumbnail" alt="Preview"/>
            <button @click="removeStagedFile(index)" class="remove-file-btn" title="移除文件">&times;</button>
          </div>
        </div>
        <textarea
         v-model="newMessage"
         @keydown.enter.prevent="sendMessage"
         placeholder="输入消息..."
         :disabled="isLoading"
        ></textarea>
      </div>
      <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" accept=".dcm,.jpg,.jpeg,.png">
            <div class="button-group">
        <button @click="triggerFileUpload" class="upload-btn" :disabled="isLoading" title="上传文件">
          📎
        </button>
        <button @click="sendMessage" class="send-btn" :disabled="isLoading || (!newMessage.trim() && stagedFiles.length === 0)">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted, onUnmounted } from 'vue';
import imageCompression from 'browser-image-compression';
import { renderMarkdown } from './markdown.js';

export default {
  name: 'Chat',
  data() {
    return {
      renderMarkdown,
      messages: [
        { sender: 'ai', text: '您好！我是您的 AI 助手，请问有什么可以帮助您的吗？' }
      ],
      newMessage: '',
      stagedFiles: [], // Array to hold staged files
      stagedFileUrls: [], // Array to hold preview URLs
      isDragging: false,
      isLoading: false,
    };
  },
  methods: {
        async sendMessage() {
      if (this.newMessage.trim() === '' && this.stagedFiles.length === 0) return;

      this.isLoading = true;
      let userMessageText = this.newMessage;
      const formData = new FormData();

            if (this.stagedFiles.length > 0) {
        this.stagedFiles.forEach(file => {
          formData.append('file', file); // Append each file
        });
        userMessageText = this.newMessage;
        if (this.newMessage) {
          formData.append('prompt', this.newMessage);
        }
      }

      const userMessage = { sender: 'user', text: userMessageText };
      this.messages.push(userMessage);
      const messageToSend = this.newMessage;
      this.newMessage = '';
            this.clearStagedFiles();

      this.$nextTick(() => {
        this.scrollToBottom();
      });

      try {
        let response;
        // If there's a file, send as multipart/form-data
        if (formData.has('file')) {
            response = await axios.post('http://127.0.0.1:3000/chat', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
        } else {
            // Otherwise, send as JSON
            response = await axios.post('http://127.0.0.1:3000/chat', {
                message: messageToSend,
            });
        }
        const aiMessage = { sender: 'ai', text: response.data.reply };
        this.messages.push(aiMessage);
      } catch (error) {
        console.error('Error communicating with the chat backend:', error);
        const errorMessage = { sender: 'ai', text: '抱歉，我现在无法回答。请稍后再试。' };
        this.messages.push(errorMessage);
      } finally {
        this.isLoading = false;
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    scrollToBottom() {
      const messagesArea = this.$refs.messagesArea;
      if (messagesArea) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
      }
    },
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    handleDrop(event) {
      this.isDragging = false;
      this.stageFiles(event.dataTransfer.files);
    },
    handleFileUpload(event) {
      this.stageFiles(event.target.files);
      // Reset file input to allow uploading the same file again
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    async stageFiles(files) {
      // Use MIME types for validation against file.type
      const allowedTypes = ['application/dicom', 'image/jpeg', 'image/png'];
      const maxFiles = 9;

      if (this.stagedFiles.length + files.length > maxFiles) {
        alert(`最多只能上传 ${maxFiles} 张图片。`);
        return;
      }

      const compressionOptions = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true,
      };

      for (const file of files) {
        if (this.stagedFiles.length >= maxFiles) break;
        if (allowedTypes.includes(file.type)) {
          try {
            const compressedFile = await imageCompression(file, compressionOptions);
            this.stagedFiles.push(compressedFile);
            const reader = new FileReader();
            reader.onload = (e) => {
              this.stagedFileUrls.push(e.target.result);
            };
            reader.readAsDataURL(compressedFile);
          } catch (error) {
            console.error('Image compression failed:', error);
            alert(`Failed to compress image: ${file.name}`);
          }
        } else {
          alert(`不支持的文件类型: ${file.name}`);
        }
      }
    },
    removeStagedFile(index) {
      URL.revokeObjectURL(this.stagedFileUrls[index]);
      this.stagedFiles.splice(index, 1);
      this.stagedFileUrls.splice(index, 1);
    },
    clearStagedFiles() {
      this.stagedFileUrls.forEach(url => URL.revokeObjectURL(url));
      this.stagedFiles = [];
      this.stagedFileUrls = [];
    },
  },
  mounted() {
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 80vh;
  max-height: 80vh;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  background-color: #f7f7f7;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

.chat-header h2 {
  margin: 0;
  font-size: 20px;
  color: #000;
}

.chat-header p {
  margin: 4px 0 0;
  color: #666;
}

.messages-area {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  max-width: 70%;
}

.message.user {
  align-self: flex-end;
}

.message.ai {
  align-self: flex-start;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 18px;
  color: white;
}

.message.user .message-bubble {
  background-color: #4A90E2;
}

.message.ai .message-bubble {
  background-color: #e5e5ea;
  color: #000;
}

.input-area {
  display: flex;
  align-items: flex-end; /* Aligns items to the bottom */
  padding: 10px;
  border-top: 1px solid #ddd;
  background-color: #fff;
  gap: 10px; /* Use gap for consistent spacing */
}

.textarea-wrapper {
  flex: 1; /* This makes the textarea wrapper take up all available space */
  display: flex;
  flex-direction: column;
}

.staged-files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}

.staged-file-preview {
  position: relative;
  width: 70px;
  height: 70px;
}

.file-thumbnail {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  object-fit: cover;
}

.file-name-preview {
  flex-grow: 1;
  font-size: 14px;
  color: #333;
  background-color: #e0e0e0;
  padding: 10px;
  border-radius: 4px;
}

.remove-file-btn {
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  line-height: 18px;
  text-align: center;
  font-size: 14px;
  cursor: pointer;
  color: #555;
  position: absolute;
  top: -5px;
  right: -5px;
}

.remove-file-btn:hover {
  background-color: #e0e0e0;
  color: #000;
}

.input-area textarea {
  flex-grow: 1;
  border: 1px solid #ccc;
  border-radius: 18px;
  padding: 10px 15px;
  resize: none;
  font-family: inherit;
  font-size: 16px;
  margin-right: 10px;
  height: 40px;
  line-height: 20px;
}

.button-group {
  display: flex;
  align-items: center;
  flex-shrink: 0; /* Prevents the button group from shrinking and wrapping */
}

.upload-btn, .send-btn {
  padding: 0 20px;
  border: none;
  background-color: #6c757d;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  height: 40px;
  line-height: 40px;
}

.upload-btn {
  margin-right: 8px;
}

.input-area button:hover:not(:disabled) {
  background-color: #357abd;
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  border: 2px dashed #fff;
  border-radius: 8px;
  z-index: 10;
}
</style>
