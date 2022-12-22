require_relative '../giftcard.rb'

describe GiftCard do
    
    it 'fails with negative balance' do
      expect { GiftCard.new(-1) }.to raise_error(ArgumentError)
    end

    it 'succeeds with positive balance' do
      gift_card = GiftCard.new(20)
      expect(gift_card.balance).to eq(20)
    end

    it 'has a test that trivially passes' do
    end

end
    