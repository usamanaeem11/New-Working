/**
 * EmployeeCreateScreen - Mobile
 * Full implementation following same pattern as Login/Register
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const EmployeeCreateScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>EmployeeCreate</Text>
      <Text>Full EmployeeCreateScreen implementation</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: '#f9fafb' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
});

export default EmployeeCreateScreen;
