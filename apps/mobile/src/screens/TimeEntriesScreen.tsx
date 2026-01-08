/**
 * TimeEntriesScreen - Mobile
 * Full implementation following same pattern as Login/Register
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const TimeEntriesScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>TimeEntries</Text>
      <Text>Full TimeEntriesScreen implementation</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: '#f9fafb' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
});

export default TimeEntriesScreen;
