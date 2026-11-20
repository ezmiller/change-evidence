(ns change-evidence.test-runner
  (:require [clojure.test :as test]
            [change-evidence.core-test]))

(defn run [_]
  (let [result (test/run-tests 'change-evidence.core-test)]
    (when (pos? (+ (:fail result) (:error result)))
      (throw (ex-info "Tests failed" result)))
    result))

