<template>
  <div class="management-container">
    <h2>患者管理</h2>

    <!-- Add Patient Form -->
    <div class="add-patient-form card">
      <h3>添加新患者</h3>
      <form @submit.prevent="addPatient">
        <div class="form-row">
          <input v-model="newPatient.name" placeholder="姓名" required>
          <input v-model.number="newPatient.age" type="number" placeholder="年龄" required>
          <select v-model="newPatient.gender">
            <option>男</option>
            <option>女</option>
            <option>其他</option>
          </select>
          <input v-model="newPatient.contact_info" placeholder="联系方式" required>
          <button type="submit" class="btn-add">添加患者</button>
        </div>
      </form>
    </div>

    <!-- Patients List -->
    <div class="table-responsive card">
      <table class="management-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>姓名</th>
            <th>年龄</th>
            <th>性别</th>
            <th>联系方式</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="patient in patients" :key="patient.id">
            <td>{{ patient.id }}</td>
            <td>{{ patient.name }}</td>
            <td>{{ patient.age }}</td>
            <td>{{ patient.gender }}</td>
            <td>{{ patient.contact_info }}</td>
            <td>{{ new Date(patient.created_at).toLocaleString() }}</td>
            <td>
              <button @click="deletePatient(patient.id)" class="btn-delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="patients.length === 0" class="empty-state">暂无患者数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const patients = ref([]);
const newPatient = ref({
  name: '',
  age: null,
  gender: '男',
  contact_info: ''
});

const fetchPatients = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:3000/patients');
    if (response.data.success) {
      patients.value = response.data.patients;
    }
  } catch (error) {
    console.error('获取患者列表失败:', error);
    alert('获取患者列表失败');
  }
};

const addPatient = async () => {
  if (!newPatient.value.name || !newPatient.value.age || !newPatient.value.contact_info) {
    alert('请完整填写患者信息');
    return;
  }
  try {
    const response = await axios.post('http://127.0.0.1:3000/patients', newPatient.value);
    if (response.data.success) {
      alert('患者添加成功');
      newPatient.value = { name: '', age: null, gender: '男', contact_info: '' };
      fetchPatients(); // Refresh the list
    } else {
      alert(response.data.message || '添加失败');
    }
  } catch (error) {
    console.error('添加患者失败:', error);
    alert('添加患者失败');
  }
};

const deletePatient = async (patientId) => {
  if (!confirm('确定要删除该患者吗？此操作不可逆。')) {
    return;
  }
  try {
    const response = await axios.delete(`http://127.0.0.1:3000/patients/${patientId}`);
    if (response.data.success) {
      alert('患者删除成功');
      fetchPatients(); // Refresh the list
    } else {
      alert(response.data.message || '删除失败');
    }
  } catch (error) {
    console.error('删除患者失败:', error);
    alert('删除患者失败');
  }
};

onMounted(fetchPatients);
</script>

<style scoped>
.management-container {
  padding: 2rem;
  background-color: #f0f2f5;
}
.card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    margin-bottom: 2rem;
}
h2, h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #000;
}
.add-patient-form .form-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.add-patient-form input, .add-patient-form select {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  flex-grow: 1;
  color: #333;
}

.add-patient-form input::placeholder {
  color: #888;
}
.btn-add {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-add:hover {
  background-color: #218838;
}
.table-responsive {
  overflow-x: auto;
}
.management-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.management-table th, .management-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
  color: #555;
}
.management-table tr:last-child td {
    border-bottom: none;
}
.management-table thead th {
  background-color: #f7f7f7;
  font-weight: 600;
  color: #333;
}
.btn-delete {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-delete:hover {
  background-color: #c0392b;
}
.empty-state {
  padding: 2rem;
  text-align: center;
  color: #777;
}
</style>
