require 'active_support/core_ext/time'
module ActiveRecord
  class Base
    class Errors
      def add(attr,str) ; end
    end
    cattr_accessor :validate_called
    attr_accessor :rating, :release_date
    attr_reader :validate_called, :errors
    def initialize(rating,release_date)
      @rating,@release_date = rating,release_date
      @errors = Errors.new
    end
    def self.validate(callable)
      @@validate_called = callable
    end
  end
end

class Movie < ActiveRecord::Base
  ???validate :rating_consistent_with_date
  def rating_consistent_with_date()
  end
end




