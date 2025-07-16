<template>
  <div class="content-section">
    <h2>管理员管理</h2>
    <div class="add-form">
      <h3>添加新管理员</h3>
      <form @submit.prevent="addAdmin">
        <input type="text" v-model="newAdmin.username" placeholder="用户名" required>
        <input type="password" v-model="newAdmin.password" placeholder="密码" required>
        <button type="submit">添加管理员</button>
      </form>
    </div>
    <div class="table-container">
      <h3>管理员列表</h3>
      <table v-if="admins.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in admins" :key="admin.id">
            <td>{{ admin.id }}</td>
            <td>{{ admin.username }}</td>
            <td>
              <button class="delete-btn" @click="deleteAdmin(admin.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">正在加载管理员列表或没有找到管理员...</p>
      <p v-if="adminError" class="error-message">{{ adminError }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminsManagement',
  data() {
    return {
      admins: [],
      newAdmin: {
        username: '',
        password: '',
      },
      adminError: null,
    };
  },
  async created() {
    this.fetchAdmins();
  },
  methods: {
    async fetchAdmins() {
      this.adminError = null;
      try {
        const response = await axios.get('http://localhost:3000/admins');
        if (response.data.success) {
          this.admins = response.data.admins;
        } else {
          this.adminError = response.data.message || '无法加载管理员列表。';
        }
      } catch (err) {
        this.adminError = '加载管理员列表时出错，请稍后再试。';
        console.error(err);
      }
    },
    async addAdmin() {
      if (!this.newAdmin.username || !this.newAdmin.password) {
        this.adminError = '用户名和密码不能为空。';
        return;
      }
      try {
        const response = await axios.post('http://localhost:3000/admins', this.newAdmin);
        if (response.data.success) {
          this.fetchAdmins(); // Refresh the list
          this.newAdmin.username = '';
          this.newAdmin.password = '';
        } else {
          this.adminError = response.data.message || '添加管理员失败。';
        }
      } catch (err) {
        this.adminError = '添加管理员时出错，请稍后再试。';
        console.error(err);
      }
    },
    async deleteAdmin(adminId) {
      if (!confirm('确定要删除这位管理员吗？')) return;
      try {
        const response = await axios.delete(`http://localhost:3000/admins/${adminId}`);
        if (response.data.success) {
          this.fetchAdmins(); // Refresh the list
        } else {
          this.adminError = response.data.message || '删除管理员失败。';
        }
      } catch (err) {
        this.adminError = '删除管理员时出错，请稍后再试。';
        console.error(err);
      }
    },
  },
};
</script>

<style scoped>
.content-section {
  padding: 24px;
}

.content-section h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #4A90E2;
  padding-bottom: 8px;
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.table-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-weight: bold;
  color: #000;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead {
  background-color: #f9fafb;
}

th, td {
  padding: 14px 18px;
  border-bottom: 1px solid #e0e0e0;
  color: #555;
}

th {
  font-weight: 600;
  color: #333;
}

tbody tr:hover {
  background-color: #f0f4f8;
}

.empty-state,
.error-message {
  text-align: center;
  padding: 40px;
  color: #777;
}

.error-message {
  color: #d9534f;
  background-color: #f2dede;
  border: 1px solid #ebccd1;
  border-radius: 8px;
}

.add-form {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.add-form h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-weight: bold;
  color: #000;
}

.add-form input {
  display: block;
  width: 100%;
  max-width: 300px;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.add-form button {
  padding: 10px 15px;
  background-color: #4A90E2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-form button:hover {
  background-color: #357ABD;
}

.delete-btn {
  padding: 5px 10px;
  background-color: #d9534f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.delete-btn:hover {
  background-color: #c9302c;
}
</style>
