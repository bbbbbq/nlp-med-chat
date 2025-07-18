<template>
  <div class="app-container">
    <!-- Tab Navigation -->
    <div class="tab-nav">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- Chat Tab -->
    <div 
      v-if="activeTab === 'chat'"
      class="chat-container"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div v-if="isDragging" class="drag-overlay">
        <p>将文件拖放到此处以上传</p>
      </div>
      <div class="chat-header">
        <h2>🩺 医疗影像分析</h2>
        <p>上传医疗影像，获得专业的症状提取和诊断建议</p>
      </div>
    <div class="messages-area" ref="messagesArea">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.sender">
        <div class="message-bubble">
          <div v-if="message.sender !== 'ai'">
            <!-- Display images if they exist -->
            <div v-if="message.images && message.images.length > 0" class="message-images">
              <img v-for="(imageUrl, imgIndex) in message.images" :key="imgIndex" 
                   :src="imageUrl" class="message-image" alt="用户上传的图片"/>
            </div>
            <!-- Display text -->
            <p v-if="message.text">{{ message.text }}</p>
          </div>
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
    
    <!-- Case Generation Tab -->
    <div v-if="activeTab === 'case'" class="case-container">
      <div class="case-header">
        <h2>📄 病例生成</h2>
        <p>基于症状描述生成模拟病例报告</p>
      </div>
      
      <div class="case-form">
        <div class="form-group">
          <label>病人基本信息</label>
          <div class="patient-info">
            <input v-model="caseForm.name" placeholder="姓名" type="text" class="form-input">
            <input v-model="caseForm.age" placeholder="年龄" type="number" class="form-input">
            <select v-model="caseForm.gender" class="form-select">
              <option value="">选择性别</option>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label>病历管理信息</label>
          <div class="patient-info">
            <input v-model="caseForm.medicalRecordNumber" placeholder="病历号" type="text" class="form-input">
            <input v-model="caseForm.visitDate" placeholder="就诊日期" type="date" class="form-input">
          </div>
          <div class="patient-info" style="margin-top: 10px;">
            <input v-model="caseForm.reportDate" placeholder="报告日期" type="date" class="form-input">
            <input v-model="caseForm.reportingPhysician" placeholder="报告医师" type="text" class="form-input">
          </div>
        </div>
        
        <div class="form-group">
          <label>主诉</label>
          <textarea 
            v-model="caseForm.chiefComplaint" 
            placeholder="请描述患者的主要症状和不适..." 
            class="form-textarea"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>现病史</label>
          <textarea 
            v-model="caseForm.presentIllness" 
            placeholder="请详细描述症状发生、发展过程..." 
            class="form-textarea"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>既往史 <span class="optional">(可选)</span></label>
          <textarea 
            v-model="caseForm.pastHistory" 
            placeholder="过往疾病史、手术史、药物过敏史等..." 
            class="form-textarea"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>体格检查 <span class="optional">(可选)</span></label>
          <textarea 
            v-model="caseForm.physicalExam" 
            placeholder="体温、血压、心率等生命体征及其他检查结果..." 
            class="form-textarea"
          ></textarea>
        </div>
        
        <!-- Medical Image Attachments -->
        <div class="form-group">
          <label>医学影像附件 <span class="optional">(可选)</span></label>
          <div class="file-upload-area">
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect"
              multiple
              accept="image/*"
              class="file-input"
              id="imageUpload"
            >
            <label for="imageUpload" class="file-upload-label">
              <div class="upload-content">
                <span class="upload-icon">📁</span>
                <span class="upload-text">点击选择或拖拽医学影像文件</span>
                <span class="upload-hint">支持 PNG, JPG, JPEG, GIF 等格式</span>
              </div>
            </label>
          </div>
          
          <!-- Selected Files Display -->
          <div v-if="selectedFiles.length > 0" class="selected-files">
            <h4>已选择的文件：</h4>
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
              <span class="file-name">📷 {{ file.name }}</span>
              <span class="file-size">({{ formatFileSize(file.size) }})</span>
              <button @click="removeFile(index)" class="remove-file-btn">✕</button>
            </div>
          </div>
        </div>
        
        <button 
          @click="generateCase" 
          class="generate-btn"
          :disabled="isGenerating || !caseForm.chiefComplaint.trim()"
        >
          <span v-if="isGenerating">🔄 生成中...</span>
          <span v-else>🏥 生成病例报告</span>
        </button>
      </div>
      
      <!-- Generated Case Report -->
      <div v-if="generatedCase" class="case-report">
        <h3>📄 生成的病例报告</h3>
        <div class="report-content" v-html="renderMarkdown(generatedCase)"></div>
        <div class="report-actions">
          <button @click="copyCase" class="action-btn">📋 复制报告</button>
          <button @click="downloadCase" class="action-btn">⬇️ 下载报告</button>
          <button @click="exportToPDF" class="action-btn" :disabled="isExportingPDF">📄 导出PDF</button>
        </div>
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
      // Tab management
      activeTab: 'chat',
      tabs: [
        { id: 'chat', name: '🩺 医疗影像分析' },
        { id: 'case', name: '📄 病例生成' }
      ],
      // Chat data
      messages: [
        { sender: 'ai', text: '您好！我是您的医疗AI助手。您可以上传医疗影像进行专业分析，或在“病例生成”选项卡中创建模拟病例报告。' }
      ],
      newMessage: '',
      stagedFiles: [], // Array to hold staged files
      stagedFileUrls: [], // Array to hold preview URLs
      isDragging: false,
      isLoading: false,
      // Case generation data
      caseForm: {
        name: '',
        age: '',
        gender: '',
        medicalRecordNumber: '',
        visitDate: '',
        reportDate: '',
        reportingPhysician: '',
        chiefComplaint: '',
        presentIllness: '',
        pastHistory: '',
        physicalExam: ''
      },
      generatedCase: '',
      isGenerating: false,
      isExportingPDF: false,
      // File upload for case generation
      selectedFiles: []
    };
  },
  methods: {
        async sendMessage() {
      if (this.newMessage.trim() === '' && this.stagedFiles.length === 0) return;

      this.isLoading = true;
      let userMessageText = this.newMessage;
      const formData = new FormData();
      const hasFiles = this.stagedFiles.length > 0;

      if (hasFiles) {
        this.stagedFiles.forEach(file => {
          formData.append('file', file); // Append each file
        });
        userMessageText = this.newMessage;
        // Always append prompt, use default if message is empty
        const promptText = this.newMessage.trim() || '请分析这张图片';
        formData.append('prompt', promptText);
      }

      // Show appropriate message text for user
      const displayText = userMessageText.trim() || (hasFiles ? '[发送了图片]' : '');
      const userMessage = { 
        sender: 'user', 
        text: displayText,
        images: hasFiles ? [...this.stagedFileUrls] : [] // Copy current image URLs
      };
      this.messages.push(userMessage);
      const messageToSend = this.newMessage;
      this.newMessage = '';
      
      // Clear staged files immediately after sending
      if (hasFiles) {
        this.clearStagedFiles();
      }

      this.$nextTick(() => {
        this.scrollToBottom();
      });

      try {
        let response;
        // If there's a file, send as multipart/form-data
        if (hasFiles) {
            response = await axios.post('http://127.0.0.1:3000/chat', formData);
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
            // Preserve the original filename
            const fileWithName = new File([compressedFile], file.name, {
              type: compressedFile.type,
              lastModified: Date.now()
            });
            this.stagedFiles.push(fileWithName);
            const reader = new FileReader();
            reader.onload = (e) => {
              this.stagedFileUrls.push(e.target.result);
            };
            reader.readAsDataURL(fileWithName);
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
    
    // Case generation methods
    async generateCase() {
      if (!this.caseForm.chiefComplaint.trim()) {
        alert('请至少填写主诉内容');
        return;
      }
      
      this.isGenerating = true;
      this.generatedCase = '';
      
      try {
        // 检查是否有文件上传
        const hasFiles = this.selectedFiles.length > 0;
        
        if (hasFiles) {
          // 如果有文件，使用FormData
          const formData = new FormData();
          
          // 添加文本数据
          formData.append('name', this.caseForm.name);
          formData.append('age', this.caseForm.age);
          formData.append('gender', this.caseForm.gender);
          formData.append('medicalRecordNumber', this.caseForm.medicalRecordNumber);
          formData.append('visitDate', this.caseForm.visitDate);
          formData.append('reportDate', this.caseForm.reportDate);
          formData.append('reportingPhysician', this.caseForm.reportingPhysician);
          formData.append('chiefComplaint', this.caseForm.chiefComplaint);
          formData.append('presentIllness', this.caseForm.presentIllness);
          formData.append('pastHistory', this.caseForm.pastHistory);
          formData.append('physicalExam', this.caseForm.physicalExam);
          
          // 添加文件
          this.selectedFiles.forEach((file, index) => {
            formData.append(`image_${index}`, file);
          });
          
          const response = await axios.post('http://127.0.0.1:3000/generate-case', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          
          if (response.data.success) {
            this.generatedCase = response.data.caseReport;
          } else {
            alert('病例生成失败：' + (response.data.message || '未知错误'));
          }
        } else {
          // 没有文件，使用JSON
          const caseData = {
            name: this.caseForm.name,
            age: this.caseForm.age,
            gender: this.caseForm.gender,
            medicalRecordNumber: this.caseForm.medicalRecordNumber,
            visitDate: this.caseForm.visitDate,
            reportDate: this.caseForm.reportDate,
            reportingPhysician: this.caseForm.reportingPhysician,
            chiefComplaint: this.caseForm.chiefComplaint,
            presentIllness: this.caseForm.presentIllness,
            pastHistory: this.caseForm.pastHistory,
            physicalExam: this.caseForm.physicalExam
          };
          
          const response = await axios.post('http://127.0.0.1:3000/generate-case', caseData);
          
          if (response.data.success) {
            this.generatedCase = response.data.caseReport;
          } else {
            alert('病例生成失败：' + (response.data.message || '未知错误'));
          }
        }
      } catch (error) {
        console.error('Case generation error:', error);
        alert('病例生成失败，请稍后重试');
      } finally {
        this.isGenerating = false;
      }
    },
    
    async copyCase() {
      try {
        await navigator.clipboard.writeText(this.generatedCase);
        alert('病例报告已复制到剪贴板');
      } catch (error) {
        console.error('Copy failed:', error);
        alert('复制失败，请手动复制');
      }
    },
    
    downloadCase() {
      const blob = new Blob([this.generatedCase], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `病例报告_${new Date().toISOString().slice(0,10)}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
    
    async exportToPDF() {
      if (!this.generatedCase) {
        alert('请先生成病例报告');
        return;
      }
      
      this.isExportingPDF = true;
      
      try {
        const response = await axios.post('http://127.0.0.1:3000/export-pdf', {
          content: this.generatedCase,
          filename: `病例报告_${new Date().toISOString().slice(0,10)}`
        }, {
          responseType: 'blob'
        });
        
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `病例报告_${new Date().toISOString().slice(0,10)}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert('PDF导出成功');
      } catch (error) {
        console.error('PDF export error:', error);
        alert('PDF导出失败，请稍后重试');
      } finally {
        this.isExportingPDF = false;
      }
    },
    
    // File handling methods for case generation
    handleFileSelect(event) {
      const files = Array.from(event.target.files);
      this.addFilesToCase(files);
    },
    
    addFilesToCase(files) {
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp'];
      
      for (const file of files) {
        if (allowedTypes.includes(file.type)) {
          if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert(`文件 ${file.name} 太大，请选择小于 10MB 的文件`);
            continue;
          }
          this.selectedFiles.push(file);
        } else {
          alert(`不支持的文件类型: ${file.name}`);
        }
      }
      
      // Clear the input value to allow selecting the same file again
      event.target.value = '';
    },
    
    removeFile(index) {
      this.selectedFiles.splice(index, 1);
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
  },
  mounted() {
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 85vh;
  max-height: 85vh;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  padding: 0;
}

.tab-btn {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #000;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-btn.active {
  color: #4A90E2;
  background-color: #fff;
  border-bottom-color: #4A90E2;
}

.tab-btn:hover {
  background-color: #e9ecef;
  color: #333;
}

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
  color: #000;
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
  color: #000;
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

/* Message images styles */
.message-images {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.message-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
}

.message-image:hover {
  transform: scale(1.05);
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

/* Case Generation Styles */
.case-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

.case-header {
  padding: 20px;
  background-color: #f7f7f7;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

.case-header h2 {
  margin: 0;
  font-size: 20px;
  color: #000;
}

.case-header p {
  margin: 4px 0 0;
  color: #000;
}

.case-form {
  padding: 20px;
  flex-grow: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.optional {
  font-weight: 400;
  color: #000;
  font-size: 14px;
}

.patient-info {
  display: flex;
  gap: 15px;
}

.form-input, .form-select {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #4A90E2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

.form-textarea {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s;
}

.form-textarea:focus {
  outline: none;
  border-color: #4A90E2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

.generate-btn {
  width: 100%;
  padding: 15px;
  background-color: #4A90E2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.generate-btn:hover:not(:disabled) {
  background-color: #357abd;
}

.generate-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.case-report {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.case-report h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.report-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 6px;
  border: 1px solid #ddd;
  margin-bottom: 15px;
  max-height: 400px;
  overflow-y: auto;
  color: #000;
}

/* 确保病例报告中的所有markdown元素都是黑色 */
.report-content h1,
.report-content h2,
.report-content h3,
.report-content h4,
.report-content h5,
.report-content h6,
.report-content p,
.report-content li,
.report-content td,
.report-content th,
.report-content span,
.report-content div {
  color: #000 !important;
}

.report-content strong,
.report-content b {
  color: #000 !important;
  font-weight: bold;
}

.report-content em,
.report-content i {
  color: #000 !important;
}

.report-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 10px 15px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
}

.action-btn:hover {
  background-color: #545b62;
}

/* File upload and selection styles */
.file-upload-area {
  margin-bottom: 15px;
}

.file-input {
  display: none;
}

.file-upload-label {
  display: block;
  padding: 20px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
  color: #000;
}

.file-upload-label:hover {
  border-color: #4A90E2;
  background-color: #f0f8ff;
}

.selected-files {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.selected-files h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #000;
  font-weight: 600;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 8px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f0f0f0;
}

.file-item:last-child {
  margin-bottom: 0;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #000;
  font-weight: 500;
}

.file-size {
  font-size: 12px;
  color: #000;
  margin-left: 8px;
  margin-right: 8px;
}

.file-item .remove-file-btn {
  position: static;
  width: 24px;
  height: 24px;
  line-height: 22px;
  font-size: 12px;
  margin-left: 8px;
}
</style>
