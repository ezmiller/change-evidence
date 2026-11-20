(ns change-evidence.core-test
  (:require [clojure.test :refer [deftest is]]
            [change-evidence.core]))

(deftest namespace-loads
  (is (find-ns 'change-evidence.core)))

