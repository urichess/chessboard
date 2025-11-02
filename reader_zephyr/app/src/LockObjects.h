#ifndef __LOCK_OBJECTS_H__
#define __LOCK_OBJECTS_H__

#include <zephyr/kernel.h>

class ScopedLock {
public:
    explicit ScopedLock(k_mutex* m)
        : mutex_(m) {
        if (mutex_) {
            k_mutex_lock(mutex_, K_FOREVER);
        }
    }

    ~ScopedLock() {
        if (mutex_) {
            k_mutex_unlock(mutex_);
        }
    }

    ScopedLock(const ScopedLock&) = delete;
    ScopedLock& operator=(const ScopedLock&) = delete;

private:
    k_mutex* mutex_ = nullptr;
};

#endif

