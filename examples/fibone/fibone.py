import siliconcompiler

def main():
    chip = siliconcompiler.Chip('mkFibOne')
    chip.set('source', 'bsv', 'FibOne.bsv')
    chip.set('frontend', 'bluespec')
    # default Bluespec clock pin is 'CLK'
    #chip.clock(name='clock', pin='CLK', period=5)
    chip.load_target('freepdk45_demo')
    chip.run()
    chip.summary()
    chip.show()

if __name__ == '__main__':
    main()
