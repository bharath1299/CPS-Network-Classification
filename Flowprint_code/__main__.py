import argparse
import argformat
import numpy as np
import os
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report
from logfile import log_resource_utilization
try:
    from .flowprint    import FlowPrint
    from .preprocessor import Preprocessor
except:
    try:
        from flowprint    import FlowPrint
        from preprocessor import Preprocessor
    except Exception as e:
        raise ValueError(e)


def fingerprint(flowprint, args):
    """Execute Flowprint in fingerprint mode"""
    ################################################################
    #                      Process input data                      #
    ################################################################
    # Initialise flows and labels
    X, y = list(), list()
    # Initialise preprocessor
    preprocessor = Preprocessor(verbose=True)

    # Parse files - if necessary
    if args.pcaps:
        # Process data
        X_, y_ = preprocessor.process(args.pcaps, args.pcaps)
        # Add data to datapoints
        X.append(X_)
        y.append(y_)

    # Load preprocessed data - if necessary
    if args.read:
        # Loop over all preprocessed files
        for infile in args.read:
            # Load each file
            X_, y_ = preprocessor.load(infile)
            # Add input file to data
            X.append(X_)
            y.append(y_)

    # Concatenate datapoints
    X = np.concatenate(X)
    y = np.concatenate(y)

    # Write preprocessed data - if necessary
    if args.write:
        # Save data
        preprocessor.save(args.write, X, y)

    ################################################################
    #               Split fingerprints if necessary               #
    ################################################################

    if args.split:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.split, random_state=args.random)
        data = [('train', X_train, y_train), ('test', X_test, y_test)]
        #splitting training and testing for checking purpose
        '''try:
            print("Saving training fingerprints...")
            with open('/home/ec2-user/training_fingerprints.json', 'w') as train_file:
                json.dump({'X': X_train.tolist(), 'y': y_train.tolist()}, train_file)
            print("Training fingerprints saved.")

            print("Saving testing fingerprints...")
            with open('/home/ec2-user/testing_fingerprints.json', 'w') as test_file:
                json.dump({'X': X_test.tolist(), 'y': y_test.tolist()}, test_file)
            print("Testing fingerprints saved.")
            if os.path.exists('/home/ec2-user/training_fingerprints.json') and \
               os.path.exists('/home/ec2-user/testing_fingerprints.json'):
                print("Data has been split and saved as 'training_fingerprints.json' and 'testing_fingerprints.json'")
        except Exception as e:
            print(f"An error occurred while saving the files: {e}")



        # Notify user
        print("Data has been split and saved as 'training_fingerprints.json' and 'testing_fingerprints.json'")

        data = [('train', X_train, y_train), ('test', X_test, y_test)]'''
    else:
        data = [('', X, y)]

    # Loop over both sets
    for type, X, y in data:

        ################################################################
        #                     Create fingerprints                      #
        ################################################################

        # Fit fingerprints
        flowprint.fit(X, y)

        # Make dictionary of label -> fingerprints
        fingerprints = dict()
        # Fill fingerprints
        for fingerprint, label in flowprint.fingerprints.items():
            # Add fingerprints
            fingerprints[label] = fingerprints.get(label, []) + [fingerprint]

        ################################################################
        #                     Output fingerprints                      #
        ################################################################

        # Output to file
        if args.fingerprint:
            # Set output file
            outfile, ext = os.path.splitext(args.fingerprint)
            outfile = "{}{}{}".format(outfile, '.' + type if type else type, ext)
            # Save fingerprints
            flowprint.save(outfile)
            # Notify user fingerprints were saved
            print("Fingerprints saved to {}".format(outfile))

        # Output to terminal
        else:
            # Select type of fingerprints to output
            print("Output {}fingerprints:".format(type + ' ' if type else type))
            # Output fingerprints
            for label, fingerprint in sorted(fingerprints.items()):
                print("{}:".format(label))
                for fp in sorted(fingerprint):
                    # Get fingerprints as set
                    print("    {}".format(fp))
                print()




if __name__ == "__main__":
    ########################################################################
    #                           Parse arguments                            #
    ########################################################################
    log_resource_utilization("program starts")

    # Create argument parser
    parser = argparse.ArgumentParser(
                prog="flowprint.py",
                description="Flowprint: Semi-Supervised Mobile-App\nFingerprinting on Encrypted Network Traffic",
                formatter_class=argformat.StructuredFormatter)

    # Output arguments
    group_output = parser.add_mutually_exclusive_group(required=False)
    group_output.add_argument('--fingerprint', type=str  , nargs='?', help="mode fingerprint generation [output to FILE]")
    group_output.add_argument('--detection'  , type=float           , help="mode unseen app detection with THRESHOLD")
    group_output.add_argument('--recognition', action='store_true'  , help="mode app recognition")

    # FlowPrint parameters
    group_flowprint = parser.add_argument_group("FlowPrint parameters")
    group_flowprint.add_argument('-b', '--batch'      , type=float, default=150, help="batch  size in seconds")
    group_flowprint.add_argument('-c', '--correlation', type=float, default=0.1, help="cross-correlation threshold")
    group_flowprint.add_argument('-s', '--similarity' , type=float, default=0.9, help="similarity        threshold")
    group_flowprint.add_argument('-w', '--window'     , type=float, default=30 , help="window size in seconds")

    # Flow data input/output agruments
    group_data_in = parser.add_argument_group("Flow data input/output")
    group_data_in.add_argument('-p', '--pcaps' , type=str,   nargs='+' , help="pcap(ng) files to run through FlowPrint")
    group_data_in.add_argument('-r', '--read'  , type=str,   nargs='+' , help="read  preprocessed data from given files")
    group_data_in.add_argument('-o', '--write' , type=str              , help="write preprocessed data to   given file")
    group_data_in.add_argument('-l', '--split' , type=float, default= 0, help="fraction of data to select for testing")
    group_data_in.add_argument('-a', '--random', type=int  , default=42, help="random state to use for split")

    # Train/test input arguments
    group_data_fps = parser.add_argument_group("Train/test input")
    group_data_fps.add_argument('-t', '--train', type=str, nargs='+', help="path to json training fingerprints")
    group_data_fps.add_argument('-e', '--test' , type=str, nargs='+', help="path to json testing  fingerprints")

    # Parse given arguments
    args = parser.parse_args()

    ########################################################################
    #                           Check arguments                            #
    ########################################################################

    # --fingerprint requires --pcaps or --read
    if not args.detection and\
       not args.recognition and\
       not args.pcaps and\
       not args.read:
        # Give help message
        print(parser.format_help())
        # Throw exception
        raise RuntimeError("--recognition requires input data, please specify "
                           "--pcaps or --read arguments.")

    # --detection or --recognition require --train and --test
    if (args.detection or args.recognition) and not (args.train and args.test):
        # Give help message
        print(parser.format_help())
        # Throw exception
        raise RuntimeError("--detection/--recognition require training and "
                           "testing fingerprints, please specify --train and "
                           "--test arguments.")

    ########################################################################
    #                           Create FlowPrint                           #
    ########################################################################

    # Create FlowPrint instance with given arguments
    flowprint = FlowPrint(
        batch       = args.batch,
        window      = args.window,
        correlation = args.correlation,
        similarity  = args.similarity
    )

    ########################################################################
    #                             Execute mode                             #
    ########################################################################
    # Fingerprint mode
    if not args.detection and not args.recognition:
        fingerprint(flowprint, args)
    # Detection/Recognition mode
    else:

        ################################################################
        #                      Load fingerprints                       #
        ################################################################
        # Load FlowPrint with train fingerprints
        flowprint.load(*args.train)
        # Load test fingerprints and labels from file
        X_test, y_test = zip(*
            flowprint.load(*args.test, store=False).items()
        )

        ################################################################
        #                         Execute mode                         #
        ################################################################
        # Detection mode
        if args.detection:
            prediction = flowprint.detect(X_test, threshold=args.detection)

        # Recognition mode
        elif args.recognition:
            prediction = flowprint.recognize(X_test)


        #testing
        '''y_test = [list(y)[0] for y in y_test]
        prediction = [list(p)[0] for p in prediction]  # Adjust according to the output format of the predictions

        # Print the classification report
        print("\nClassification Report:\n")
        print(classification_report(y_test, prediction))'''

        ################################################################
        #                         Show result                          #
        ################################################################
        #added for calculating the precison, recall etc..
        #y_true_list = []
        #y_pred_list = []
        # Convert y_test and predictions to lists for metric calculations
        y_test_list = [list(y)[0] for y in y_test]
        y_pred_list = [list(y)[0] if args.recognition else y for y in prediction]

        # Calculate metrics
        accuracy = accuracy_score(y_test_list, y_pred_list)
        precision = precision_score(y_test_list, y_pred_list, average='weighted', zero_division=0)
        recall = recall_score(y_test_list, y_pred_list, average='weighted', zero_division=0)
        f1 = f1_score(y_test_list, y_pred_list, average='weighted', zero_division=0)

        # Print the metrics
        print("\nPerformance metrics:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")



        y_current = None
        # Loop over all fingerprints sorted by input label
        for fp, y_test_, y_pred_ in sorted(zip(X_test, y_test, prediction),
                                            key=lambda x: list(x[1])):
            # Get label of fingerprint
            y_test_ = list(y_test_)[0]
            # Print label if new one is found
            if y_test_ != y_current:
                print('\n',y_test_)
                y_current = y_test_

            # Output result
            if args.recognition:
                y_pred_ = list(y_pred_)[0]
            print("    {} --> {}".format(fp, y_pred_))
           # y_true_list.append(y_test_)
           # y_pred_list.append(y_pred_)

        ################################################################
        #                 Calculate Metrics after Loop                 #
        ################################################################
        # Calculate accuracy, precision, recall, and F1 score
        '''accuracy = accuracy_score(y_true_list, y_pred_list)
        precision = precision_score(y_true_list, y_pred_list, average='weighted')
        recall = recall_score(y_true_list, y_pred_list, average='weighted')
        f1 = f1_score(y_true_list, y_pred_list, average='weighted')

        # Output the metrics
        print("\nMetrics:")
        print("Accuracy:  {:.2f}%".format(accuracy * 100))
        print("Precision: {:.2f}%".format(precision * 100))
        print("Recall:    {:.2f}%".format(recall * 100))
        print("F1-Score:  {:.2f}%".format(f1 * 100))'''
        log_resource_utilization("program ends")
