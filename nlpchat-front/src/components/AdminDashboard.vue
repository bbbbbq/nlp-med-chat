<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3>管理菜单</h3>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li :class="{ active: activeTab === 'chat' }" @click="activeTab = 'chat'">
            <a href="#">智能对话</a>
          </li>
          <li :class="{ active: activeTab === 'patients' }" @click="activeTab = 'patients'">
            <a href="#">患者管理</a>
          </li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'doctors' }" @click="activeTab = 'doctors'">
            <a href="#">医生管理</a>
          </li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'admins' }" @click="activeTab = 'admins'">
            <a href="#">管理员管理</a>
          </li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'stats' }" @click="activeTab = 'stats'">
            <a href="#">系统数据统计</a>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <div class="dashboard-card">
        <header class="dashboard-header">
          <h1>管理员仪表盘</h1>
          <p>欢迎回来, 在这里管理系统数据。</p>
        </header>

        <!-- Dynamic Component View -->
        <div class="content-section">
          <chat v-if="activeTab === 'chat'"></chat>
          <patients-management v-if="activeTab === 'patients'"></patients-management>
          <doctors-management v-if="userRole === 'admin' && activeTab === 'doctors'"></doctors-management>
          <admins-management v-if="userRole === 'admin' && activeTab === 'admins'"></admins-management>
          <system-stats v-if="userRole === 'admin' && activeTab === 'stats'"></system-stats>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';

const Chat = defineAsyncComponent(() => import('./Chat.vue'));
const PatientsManagement = defineAsyncComponent(() => import('./PatientsManagement.vue'));
const DoctorsManagement = defineAsyncComponent(() => import('./DoctorsManagement.vue'));
const AdminsManagement = defineAsyncComponent(() => import('./AdminsManagement.vue'));
const SystemStats = defineAsyncComponent(() => import('./SystemStats.vue'));

export default {
  name: 'AdminDashboard',
  components: {
    Chat,
    PatientsManagement,
    DoctorsManagement,
    AdminsManagement,
    SystemStats,
  },
  data() {
    return {
      userRole: null,
      activeTab: '',
    };
  },
  created() {
    this.userRole = localStorage.getItem('userRole');
    if (this.userRole === 'admin') {
      this.activeTab = 'doctors';
    } else if (this.userRole === 'doctor') {
      this.activeTab = 'chat';
    } else {
      // Optional: Handle cases where role is not set or invalid
      this.$router.push('/login');
    }
  },
};
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f4f7f6;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.sidebar {
  width: 240px;
  background-color: #2c3e50;
  color: #ecf0f1;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  background-color: #34495e;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 20px;
  color: #ecf0f1;
  font-weight: 700;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  cursor: pointer;
  transition: background-color 0.3s;
}

.sidebar-nav a {
  display: block;
  padding: 18px 20px;
  color: #ecf0f1;
  text-decoration: none;
  font-size: 16px;
}

.sidebar-nav li:hover {
  background-color: #34495e;
}

.sidebar-nav li.active {
  background-color: #4A90E2;
}

.sidebar-nav li.active a {
  font-weight: 600;
}

.main-content {
  flex-grow: 1;
  padding: 40px;
  overflow-y: auto;
}

.dashboard-card {
  width: 100%;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.dashboard-header {
  background-color: #4A90E2;
  color: white;
  padding: 24px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 28px;
}

.dashboard-header p {
  margin: 8px 0 0;
  opacity: 0.9;
}

.content-section {
  padding: 24px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #777;
}
</style>
