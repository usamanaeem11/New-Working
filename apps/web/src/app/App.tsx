import React from 'react';
import {SafeAreaView, ScrollView, StatusBar, StyleSheet, Text, View} from 'react-native';

function App(): JSX.Element {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <ScrollView contentInsetAdjustmentBehavior="automatic">
        <View style={styles.content}>
          <Text style={styles.title}>Working Tracker</Text>
          <Text style={styles.subtitle}>Mobile App</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#fff'},
  content: {padding: 24, alignItems: 'center'},
  title: {fontSize: 32, fontWeight: 'bold', marginBottom: 8},
  subtitle: {fontSize: 18, color: '#666'},
});

export default App;
