package org.fuorigiri.performancelab

import android.content.Context
import androidx.work.*
import java.util.concurrent.TimeUnit

class SyncWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result = try {
        val success = synchronized(Runtime.lock) { Runtime.get(applicationContext).callAttr("sync_all").toBoolean() }
        if (success) Result.success() else if (runAttemptCount < 4) Result.retry() else Result.failure()
    } catch (_: Exception) { if (runAttemptCount < 4) Result.retry() else Result.failure() }

    companion object {
        fun schedule(context: Context) {
            val work = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
                .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).setRequiresBatteryNotLow(true).build())
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS).build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork("fuorigiri-webdav", ExistingPeriodicWorkPolicy.KEEP, work)
        }
        fun cancel(context: Context) { WorkManager.getInstance(context).cancelUniqueWork("fuorigiri-webdav") }
    }
}
