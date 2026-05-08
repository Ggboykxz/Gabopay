import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native'
import { router } from 'expo-router'

const stats = [
  { label: 'Balance', value: '850,000 XAF' },
  { label: 'Today', value: '45,000 XAF' },
  { label: 'Success', value: '98.2%' },
]

const transactions = [
  { id: '1', amount: '15,000 XAF', status: 'success', time: '2 min ago' },
  { id: '2', amount: '8,500 XAF', status: 'success', time: '15 min ago' },
  { id: '3', amount: '5,000 XAF', status: 'pending', time: '1 hour ago' },
]

export default function DashboardScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard</Text>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>M</Text>
        </View>
      </View>

      <View style={styles.statsContainer}>
        {stats.map((stat, index) => (
          <View key={index} style={styles.statCard}>
            <Text style={styles.statLabel}>{stat.label}</Text>
            <Text style={styles.statValue}>{stat.value}</Text>
          </View>
        ))}
      </View>

      <TouchableOpacity style={styles.scanButton} onPress={() => router.push('/scan')}>
        <Text style={styles.scanButtonText}>Scan QR Code</Text>
      </TouchableOpacity>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
          <TouchableOpacity onPress={() => router.push('/transactions')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        {transactions.map((tx) => (
          <View key={tx.id} style={styles.transactionItem}>
            <View>
              <Text style={styles.txAmount}>{tx.amount}</Text>
              <Text style={styles.txTime}>{tx.time}</Text>
            </View>
            <Text style={[styles.txStatus, tx.status === 'success' ? styles.success : styles.pending]}>
              {tx.status}
            </Text>
          </View>
        ))}
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#009e60',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    color: '#fff',
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 4,
  },
  scanButton: {
    margin: 16,
    backgroundColor: '#009e60',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  section: {
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  seeAll: {
    color: '#009e60',
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
  },
  txAmount: {
    fontSize: 16,
    fontWeight: '600',
  },
  txTime: {
    fontSize: 12,
    color: '#666',
  },
  txStatus: {
    fontSize: 12,
    fontWeight: '500',
  },
  success: {
    color: '#16a34a',
  },
  pending: {
    color: '#ca8a04',
  },
})